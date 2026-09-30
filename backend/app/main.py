from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .api.routes import router as api_router
from .auth.google import router as auth_router
from .config import get_settings
from .database import Base, engine
from .events.pubsub import router as events_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # Development bootstrap; use Alembic migrations in deployment.
    yield

app = FastAPI(title="Mail Automation", version="0.0.0", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=get_settings().app_secret, https_only=False)
app.add_middleware(CORSMiddleware, allow_origins=[get_settings().frontend_url], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(events_router)
