from pydantic import BaseModel


class UserRead(BaseModel):
    id: int | None = None
    email: str


class UserCreate(BaseModel):
    email: str
    password: str
