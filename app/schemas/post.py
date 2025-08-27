from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    body: str


class PostRead(PostCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class CommentCreate(BaseModel):
    body: str


class CommentRead(CommentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    user_id: int


class PostWithComments(BaseModel):
    post: PostRead
    comments: list[CommentRead]


class LikeCreate(BaseModel):
    post_id: int


class LikeRead(LikeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
