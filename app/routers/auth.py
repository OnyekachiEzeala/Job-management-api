from typing import Annotated
from app.logger import get_logger
from app.services.auth import AuthService, user_auth
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.schemas.staff import StaffCreate, StaffLogin, StaffResponse, Token, TokenPair
from app.database import get_db
from app.security import get_current_user

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.post("/register", response_model=StaffResponse, status_code=201)
def register(staff_create: StaffCreate, db: Session = Depends(get_db)):
    logger.info(f"Registering new staff with email: {staff_create.email}")
    try:
        new_staff = user_auth.register(db, staff_create)
        if not new_staff:
           logger.warning(f"Registration failed: User with email {staff_create.email} already exists.")
           raise HTTPException(status_code=400, detail="Email already registered")
        db.commit()
        logger.info(f"Staff with email {staff_create.email} successfully registered.")
        return new_staff
    except Exception :
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error during registration for email {staff_create.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")
    
@router.post("/login", response_model=TokenPair)
def login_user(user: StaffLogin, db: Session = Depends(get_db)):
    logger.info(f"User login attempt: {user.email}")
    access_token = user_auth.login_user(db, user)
    refresh_token = user_auth.refresh_token(db, user)
    if not access_token:
        logger.warning(f"Login failed for email: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logger.info(f"User logged in successfully with email: {user.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh_token(x_refresh_token: str = Header(...)):
    logger.info("Token refresh attempt")
    new_access_token = user_auth.refresh_access_token(x_refresh_token)
    if not new_access_token:
        logger.warning("Token refresh failed: Invalid refresh token")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    logger.info("Token refreshed successfully")
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/me", response_model=StaffResponse)
async def read_current_user(current_user: Annotated[StaffResponse, Depends(get_current_user)]):
    logger.info(f"Fetching current user info for email: {current_user.email}")
    return current_user 