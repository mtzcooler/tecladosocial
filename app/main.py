from fastapi import FastAPI
from app.routers.post import router as post_router
from app.routers.comment import router as comment_router

app = FastAPI()

app.include_router(post_router)
app.include_router(comment_router)
