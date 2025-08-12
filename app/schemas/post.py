from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    body: str


class PostRead(PostCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CommentCreate(BaseModel):
    body: str


class CommentRead(CommentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int


class PostWithComments(BaseModel):
    post: PostRead
    comments: list[CommentRead]
