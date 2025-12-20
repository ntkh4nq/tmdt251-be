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

router = APIRouter(prefix="/user", tags=["User"])


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
