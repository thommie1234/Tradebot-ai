"""Authentication routes with JWT + TOTP."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import pyotp
from datetime import datetime, timedelta
import os

router = APIRouter()
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
TOTP_SECRET = os.getenv("TOTP_SECRET")

class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: str

@router.post("/login")
async def login(req: LoginRequest):
    """Login with username/password + TOTP."""
    # Simplified: check environment variables
    valid_user = os.getenv("ADMIN_USER", "admin")
    valid_pass = os.getenv("ADMIN_PASS", "change-me")
    
    if req.username != valid_user or req.password != valid_pass:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify TOTP if configured
    if TOTP_SECRET:
        totp = pyotp.TOTP(TOTP_SECRET)
        if not totp.verify(req.totp_code):
            raise HTTPException(status_code=401, detail="Invalid TOTP code")
    
    # Generate JWT
    payload = {
        "sub": req.username,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
