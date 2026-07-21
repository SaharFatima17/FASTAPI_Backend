from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth_endpoints import router as auth_router
from app.api.v1.ws_endpoints import router as ws_router
from app.api.v1.chat_endpoints import router as chat_router  # 👈 1. Naya router import kiya

# --- DATABASE SETUP ---
from app.core.database import engine, Base
from app.models import User, ChatSession, ChatMessage 
from app.api.rag_router import router as rag_router

# 1. Pehle FastAPI app instance banayenge
app = FastAPI(
    title="Zylo Enterprise Core API", 
    description="Multi-layered High Performance Decoupled Architecture Backend Server",
    version="1.0.0"
)

# 2. Phir Database tables create honge
Base.metadata.create_all(bind=engine)

# Next.js Frontend kyonki alag se chalayengi, isliye CORS enable karna lazmi hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production mein Next.js ka specific port likhenge
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Phir sare routers (jin mein rag_router bhi shamil hai) register honge
app.include_router(auth_router, prefix="/api/v1")
app.include_router(ws_router)
app.include_router(chat_router, prefix="/api/v1")  # 👈 2. Naye chat_router ko yahan register kiya
app.include_router(rag_router, prefix="/api/v1")  # 👈 Rag router ko bhi yahan include kar dein

@app.get("/")
def health_check():
    return {"status": "healthy", "architecture": "layered-enterprise"}