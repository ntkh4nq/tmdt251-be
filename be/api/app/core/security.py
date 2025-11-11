from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, UTC
from app.core.config import SEC_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], DeprecationWarning="auto")
ALGO = "HS256"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hased: str) -> bool:
    return pwd_context.verify(plain, hased)

def create_access_token(data: dict):
    encoded = data.copy()
    expire = datetime.now(UTC)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded.update({"exp": expire})
    return jwt.encode(encoded, SEC_KEY, algorithm=ALGO)