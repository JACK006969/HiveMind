from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis

from app.core.config import settings
from app.api.routes import router, auth_router  # ✅ Import both routers
from app.models.database import engine, Base

# Create tables on startup
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🚀 {settings.APP_NAME} starting...")
    app.state.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield
    # Shutdown
    await app.state.redis.close()
    print("👋 Application shutdown complete")

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Crypto Trading Copilot",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")  # ✅ ADD THIS LINE

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
