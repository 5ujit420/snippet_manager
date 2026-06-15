from pydantic import BaseModel, ConfigDict


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class RegisterIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str


class SnippetIn(BaseModel):
    title: str
    code: str
    language: str
    tags: list[str] = []


class SnippetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    code: str
    language: str
    owner_id: int
    tags: list[TagOut] = []


class PaginatedSnippets(BaseModel):
    total: int
    page: int
    limit: int
    items: list[SnippetOut]
