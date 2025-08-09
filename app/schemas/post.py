from pydantic import BaseModel


class PostCreate(BaseModel):
    body: str


class PostRead(PostCreate):
    id: int
