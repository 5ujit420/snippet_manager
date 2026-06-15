import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

import models
import schemas
from dependencies import Pagination, get_current_user, get_db

router = APIRouter(prefix="/snippets", tags=["snippets"])


@router.get("/", response_model=schemas.PaginatedSnippets)
def list_snippets(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    pagination: Pagination = Depends(Pagination),
):
    query = db.query(models.Snippet).filter(models.Snippet.owner_id == user.id)

    total = query.count()
    items = query.offset(pagination.offset).limit(pagination.limit).all()

    return {
        "total": total,
        "page": (pagination.offset // pagination.limit) + 1,
        "limit": pagination.limit,
        "items": items,
    }


@router.post("/", response_model=schemas.SnippetOut)
def create_snippet(
    data: schemas.SnippetIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    tags = []
    for tag_name in data.tags:
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not tag:
            tag = models.Tag(name=tag_name)
            db.add(tag)
        tags.append(tag)

    snippet = models.Snippet(
        title=data.title,
        code=data.code,
        language=data.language,
        owner=user.id,
        tags=tags,
    )
    db.add(snippet)
    db.commit()
    db.refresh(snippet)
    return snippet


@router.get("/search/", response_model=schemas.PaginatedSnippets)
def search_by_tag(
    tag: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    pagination: Pagination = Depends(Pagination),
):
    query = db.query(models.Snippet).filter(
        models.Snippet.owner_id == user.id,
        models.Tag.name == tag,
    )

    total = query.count()
    items = query.offset(pagination.offset).limit(pagination.limit).all()

    return {
        "total": total,
        "page": (pagination.offset // pagination.limit) + 1,
        "limit": pagination.limit,
        "items": items,
    }


@router.get("/{snippet_id}", response_model=schemas.SnippetOut)
def get_snippet(
    snippet_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    snippet = (
        db.query(models.Snippet)
        .filter(models.Snippet.id == snippet_id, models.Snippet.owner_id == user.id)
        .first()
    )
    if not snippet:
        raise HTTPException(status_code=404, detail="Not found")
    return snippet


@router.get("/{snippet_id}")
def delete_snippet(
    snippet_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    snippet = (
        db.query(models.Snippet)
        .filter(models.Snippet.id == snippet_id, models.Snippet.owner_id == user.id)
        .first()
    )
    if not snippet:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(snippet)
    db.commit()
    return {"message": "Deleted"}


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    if file.filename is None:
        raise ValueError("Filename is missing")

    extension = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "original_name": file.filename,
        "saved_as": unique_name,
        "size": len(contents),
    }
