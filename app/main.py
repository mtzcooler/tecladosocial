from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from app.logging_config import configure_logging
from app.database import database
from app.routers.post import router as post_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(post_router)
