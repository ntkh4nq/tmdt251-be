from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hased: str) -> bool:
    return pwd_context.verify(plain, hased)

def create_access_token(data: dict, settings: dict) -> str:
    encoded = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(minutes=settings["ACCESS_TOKEN_EXPIRE_MINUTES"])
    encoded.update({"exp": expire})
    return jwt.encode(encoded, settings["SEC_KEY"], algorithm=settings["ALGO"])

def create_refresh_token(data: dict, settings: dict) -> str:
    encoded = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(days=settings["REFRESH_TOKEN_EXPIRE_DAYS"])
    encoded.update({"exp": expire})
    return jwt.encode(encoded, settings["SEC_KEY"], algorithm=settings["ALGO"])