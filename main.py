from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from routers import auth, snippets, tags

Base.metadata.create_all(engine)

app = FastAPI(title="Snippet Manager")

app.include_router(auth.router)
app.include_router(snippets.router)
app.include_router(tags.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
