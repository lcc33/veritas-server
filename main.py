from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

# Import routers correctly - use absolute imports
from api.endpoints.health import router as health_router
from api.endpoints.analyze import router as analyze_router

app = FastAPI(
    title=settings.app_name,
    description="Veritas Backend - AI-Powered Fact Checking API", 
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "https://veritas-beryl.vercel.app/",
]
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(analyze_router, prefix="/api", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Veritas Backend API", "version": "1.0.0"}
