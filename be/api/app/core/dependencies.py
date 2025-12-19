import os
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError
from app.models.user import User
import ssl

load_dotenv()

oauth2_scheme = HTTPBearer()


def get_settings():
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "ALGO": os.getenv("ALGO"),
        "SEC_KEY": os.getenv("SEC_KEY"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
        "REFRESH_TOKEN_EXPIRE_DAYS": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")),
    }


def get_vnpay_config():
    return {
        "vnp_TmnCode": os.getenv("VNP_TMNCODE"),
        "vnp_HashSecret": os.getenv("VNP_HASHSECRET"),
        "vnp_Url": os.getenv("VNP_URL"),
        "vnp_ReturnUrl": os.getenv("VNP_RETURNURL"),
        "vnp_ExpiredDate": os.getenv("VNP_EXPIRED"),
    }


database_url = os.getenv("DATABASE_URL").replace(
    "postgresql://", "postgresql+asyncpg://"
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

engine = create_async_engine(database_url, connect_args={"ssl": ctx})
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    session: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    settings: dict = Depends(get_settings),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token.credentials,
            key=settings["SEC_KEY"],
            algorithms=[settings["ALGO"]],
        )
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise credentials_exception

    result = await session.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user
