from pydantic import BaseModel


class User(BaseModel):
    id: int | None = None
    email: str


class UserCreate(User):
    password: str
