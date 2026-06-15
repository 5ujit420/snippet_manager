import os
from datetime import timezone
from typing import cast

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy.orm import Session

from database import SessionLocal

load_dotenv()

SECRET_KEY = cast(str, os.getenv("SECRET_KEY"))
assert SECRET_KEY, "SECRET_KEY is not set in environment"
ALGORITHM = "HS256"

pwd_context = PasswordHash((Argon2Hasher(),))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(username: str) -> str:
    from datetime import datetime, timedelta

    payload = {"sub": username, "exp": datetime.now(timezone.utc) + timedelta(hours=6)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    import models

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invaild token")

    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


class Pagination:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        limit: int = Query(default=10, ge=1, le=100),
    ):
        self.offset = (page - 1) * limit
        self.limit = limit
