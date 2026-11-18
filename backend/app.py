from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import create_db
from backend.ai_assitant.endpoints import ai_assistant
from.endpoints import router as endpoints_router
from .auth.apis import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth)
app.include_router(endpoints_router)
app.include_router(ai_assistant)