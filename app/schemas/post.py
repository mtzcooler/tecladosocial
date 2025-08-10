from pydantic import BaseModel


class PostCreate(BaseModel):
    body: str


class PostRead(PostCreate):
    id: int


class CommentCreate(BaseModel):
    body: str


class CommentRead(CommentCreate):
    id: int
    post_id: int


class PostWithComments(BaseModel):
    post: PostRead
    comments: list[CommentRead]
