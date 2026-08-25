from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.db.database import init_db
@asynccontextmanager
async def lifespan(app):
    await init_db(); yield
app=FastAPI(title=settings.app_name,version="1.0.0",lifespan=lifespan)
app.include_router(router,prefix="/api/v1")
@app.get("/")
async def root(): return {"service":settings.app_name,"docs":"/docs"}
