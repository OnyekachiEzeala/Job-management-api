from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logger import get_logger
from app.routers.auth import router as auth_router

logger = get_logger(__name__)

app = FastAPI(
    title="Job Management API",
    description="API for managing jobs and staff in an opeaations company",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Job Management API"}

app.include_router(auth_router)