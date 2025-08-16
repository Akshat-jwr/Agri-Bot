from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.routes import auth, users, queries, health

# App startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🌾 Starting {settings.APP_NAME}...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    🌾 **Agricultural Intelligence API**
    
    A modular, scalable API for Indian farmers providing:
    - User authentication with email verification
    - Agricultural advice and recommendations  
    - Weather and market information
    - Personalized crop guidance
    
    **Get started:** Register with just email and password!
    """,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["🏠 General"])
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["🔐 Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["👥 Users"])
app.include_router(queries.router, prefix=f"{settings.API_V1_PREFIX}/queries", tags=["🌾 Agricultural Queries"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
