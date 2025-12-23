from fastapi import APIRouter, Depends, HTTPException, Request, Body
from app.models.user import User, Session
from app.schemas.user import UserCreate, UserLoginRequest, UserOut
from app.core.dependencies import get_current_user, get_db, get_settings, engine
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.services.utils import commit_to_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from datetime import datetime, timedelta, timezone
import os
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse

router = APIRouter(prefix="/user", tags=["User"])

# Initialize OAuth client for Google
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@router.post("/register-user", response_model=dict)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    email = await db.execute(select(User.email).where(User.email == data.email))
    email = email.scalar_one_or_none()
    if email:
        raise HTTPException(
            status_code=400, detail=f"Email {email} is already registered"
        )

    hashed_password = hash_password(data.password)
    new_user = User(
        fullname=data.fullname,
        email=data.email,
        phone=data.phone,
        password_hashed=hashed_password,
    )
    db.add(new_user)
    await commit_to_db(db)
    await db.refresh(new_user)
    return {"message": f"registered user with email {new_user.email}"}


@router.post("/login", response_model=dict)
async def login_user(
    data: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    settings: dict = Depends(get_settings),
):
    user = await db.execute(select(User).where(User.email == data.email))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=404, detail="User email not found, please register"
        )

    if not verify_password(data.password, user.password_hashed):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token: str = create_access_token(data={"sub": user.email}, settings=settings)

    refresh_token: str = create_refresh_token(
        data={"sub": user.email}, settings=settings
    )
    device_info: str = request.headers.get("User-Agent", "unknown device")
    expried_at: datetime = datetime.now(timezone.utc) + timedelta(
        days=settings["REFRESH_TOKEN_EXPIRE_DAYS"]
    )
    new_session = Session(
        refresh_token=refresh_token,
        device_info=device_info,
        expired_at=expried_at,
        user_id=user.id,
    )
    db.add(new_session)
    await commit_to_db(db)
    await db.refresh(new_session)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh-session", response_model=dict)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),  # {"refresh_token": "..."}
    db: AsyncSession = Depends(get_db),
    settings: dict = Depends(get_settings),
):
    session = await db.execute(
        select(Session).where(Session.refresh_token == refresh_token)
    )
    session = session.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if session.expired_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = await db.execute(select(User).where(User.id == session.user_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token(data={"sub": user.email}, settings=settings)

    # new_refresh_token = create_refresh_token(data={"sub": user.email}, settings=settings)
    # session.refresh_token = new_refresh_token
    # session.expired_at = datetime.now(timezone.utc) + timedelta(days=settings["refresh_token_expire_days"])
    # await commit_to_db(db)
    # return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    return {"access_token": new_access_token}


@router.delete("/logout", response_model=dict)
async def logout(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session_query = await db.execute(
        select(Session).where(
            and_(
                Session.refresh_token == refresh_token,
                Session.user_id == current_user.id,
            )
        )
    )
    session = session_query.scalar_one_or_none()
    if session:
        await db.delete(session)
        await commit_to_db(db)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.get("/auth/google/login")
async def google_login(request: Request):
    """Redirect user to Google login page"""
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/user/auth/google/callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
    settings: dict = Depends(get_settings)
):
    """Handle Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        fullname = user_info.get('name', email.split('@')[0])
        
        # Check if user exists
        result = await db.execute(
            select(User).where(
                (User.google_id == google_id) | (User.email == email)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                fullname=fullname,
                google_id=google_id,
                password_hashed=None,  # No password for Google users
                is_active=True
            )
            db.add(user)
            await commit_to_db(db)
            await db.refresh(user)
        elif not user.google_id:
            # Link existing email account with Google
            user.google_id = google_id
            await commit_to_db(db)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.email}, settings=settings)
        refresh_token = create_refresh_token(data={"sub": user.email}, settings=settings)
        
        # Create session
        device_info = request.headers.get("User-Agent", "Google OAuth")
        expired_at = datetime.now(timezone.utc) + timedelta(days=settings["REFRESH_TOKEN_EXPIRE_DAYS"])
        
        new_session = Session(
            refresh_token=refresh_token,
            device_info=device_info,
            expired_at=expired_at,
            user_id=user.id
        )
        db.add(new_session)
        await commit_to_db(db)
        
        # Redirect to frontend with tokens (or return JSON for API)
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google auth failed: {str(e)}")
