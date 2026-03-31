from app.logger import get_logger
from sqlalchemy.orm import Session
from app import models
from app.schemas.staff import StaffCreate, StaffLogin, StaffResponse
from app.security import create_access_token,  create_refresh_token, get_password_hash, authenticate_user
from jose import jwt, JWTError
from fastapi import Header, HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

logger = get_logger(__name__)

class AuthService:
    @staticmethod
    def register(db: Session, staff_create: StaffCreate) -> StaffResponse:
        existing_user = (
            db.query(models.Staff)
            .filter(models.Staff.email == staff_create.email)
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(staff_create.password)
        new_staff = models.Staff(
            name=staff_create.name,
            email=staff_create.email,
            password_hash=hashed_password,
            role=staff_create.role.value
        )
        db.add(new_staff)
        db.flush()
        db.refresh(new_staff)

        logger.info(f"New staff registered: {new_staff.email}")
        return StaffResponse.model_validate(new_staff)
    
    @staticmethod   
    def login_user(db: Session, staff_login=StaffLogin):
        user = authenticate_user(staff_login.email, staff_login.password, db)
        if not user:
            logger.warning(f"Failed login attempt for email: {staff_login.email}")
            return None

        access_token = create_access_token(sub=user.email, roles=user.role)
        return access_token
    
    @staticmethod
    def refresh_token(db: Session, staff_login: StaffLogin):
        db_user = authenticate_user(staff_login.email, staff_login.password, db)
        if not db_user:
            logger.warning(f"Refresh token request for unknown email: {staff_login.email}")
            return None
        user_role = db_user.role
        refresh = create_refresh_token(sub=db_user.email, roles=user_role)
        return refresh
    
    @staticmethod
    def refresh_access_token(x_refresh_token: str = Header(...)):

        try:
            payload = jwt.decode(
                x_refresh_token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )

            # Ensure this is indeed a refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Not a refresh token")

            sub = payload.get("sub")
            role = payload.get("role")

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        new_access = create_access_token(sub=sub, roles=role)

        return new_access
    
user_auth = AuthService()