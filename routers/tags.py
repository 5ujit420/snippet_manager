from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
import schemas
from dependencies import get_current_user, get_db

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=list[schemas.TagOut])
def list_tags(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Tag).all()
