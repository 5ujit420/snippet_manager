from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
from dependencies import create_token, get_db, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/")
def register(data: schemas.RegisterIn, db: Session = Depends(get_db)):
    existing = (
        db.query(models.User).filter(models.User.username == data.username).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username taken")

    user = models.User(
        username=data.username, password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    return {"message": f"User {data.username} created"}


@router.post("/login/", response_model=schemas.LoginOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form.username).first()
    if not user or not verify_password(form.password, str(user.password_hash)):
        raise HTTPException(status_code=401, detail="Wrong Credentials")
    return {"access_token": create_token(str(user.username)), "token_type": "bearer"}
