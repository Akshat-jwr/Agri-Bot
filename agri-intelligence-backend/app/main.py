from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.routes import rag_routes, auth, users, health, chat

# App startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🌾 Starting {settings.APP_NAME}...")
    await init_db()
    print("✅ Database initialized")
    
    # Train ML models on startup
    print("🤖 Initializing ML models...")
    try:
        from app.tools.model_startup import initialize_models
        success = await initialize_models()
        if success:
            print("✅ ML models ready")
        else:
            print("⚠️  ML models using fallback mode")
    except Exception as e:
        print(f"⚠️  ML model initialization failed: {e}")
        print("🔄 Continuing with fallback models...")
    
    yield
    # Shutdown
    print("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    🌾 **Agricultural Intelligence API**
    
    A comprehensive, production-ready API for Indian farmers providing:
    
    **🔐 Authentication System:**
    - User registration with email verification
    - Secure JWT-based authentication
    - Password protection and security
    
    **🤖 AI-Powered Agricultural Intelligence:**
    - RAG (Retrieval-Augmented Generation) system
    - ML-based yield prediction (R² = 0.996 accuracy)
    - Intelligent query classification and routing
    - Real-time weather and market data integration
    
    **� Advanced Chat System:**
    - Session-based conversations with AI
    - Multi-language support for all Indian languages
    - Conversation history and context awareness
    - Message feedback and analytics
    
    **�👤 User Management:**
    - Profile management with location data
    - Crop preferences and farming details
    - Personalized recommendations
    
    **🏥 System Health:**
    - Health monitoring and diagnostics
    - Model performance tracking
    
    **Get started:** Register with email/password → Verify email → Login → Ask agricultural questions!
    
    **Demo accounts (auto-verified):**
    - `demo@farmer.com` / `demo123`
    - `test@agri.com` / `test123`
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

# Include routers - Authentication, Users, Chat, and RAG system
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["🔐 Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["👤 Users"])  
app.include_router(chat.router, prefix=f"{settings.API_V1_PREFIX}", tags=["💬 Agricultural Chat"])
app.include_router(health.router, prefix=f"{settings.API_V1_PREFIX}/health", tags=["🏥 Health"])
app.include_router(rag_routes.router, prefix=f"{settings.API_V1_PREFIX}", tags=["🌾 Agricultural Intelligence"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
