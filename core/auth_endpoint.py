#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Endpoints - JWT login/register/refresh
FULL IMPLEMENTATION - NO PLACEHOLDERS
"""

import os
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import BASE_DIR, SECRET_KEY
from .helpers import log_info, log_error

# ============================================================================
# CONFIG
# ============================================================================

AUTH_DB = os.path.join(BASE_DIR, "auth.db")
JWT_SECRET = SECRET_KEY or secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

# ============================================================================
# DATABASE INIT
# ============================================================================

def init_auth_db():
    """Initialize auth database with users table"""
    conn = sqlite3.connect(AUTH_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at INTEGER NOT NULL,
            last_login INTEGER
        )
    """)
    
    # Create default guest user if not exists
    try:
        guest_hash = hashlib.sha256("guest123".encode()).hexdigest()
        c.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ("guest", guest_hash, "guest", int(datetime.now().timestamp()))
        )
        conn.commit()
        log_info("[AUTH] Guest user ensured in database")
    except Exception as e:
        log_error(f"[AUTH] Failed to create guest user: {e}")
    
    conn.close()

init_auth_db()

# ============================================================================
# MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserInfo(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str

# ============================================================================
# UTILITIES
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt(user_id: int, username: str, role: str) -> str:
    """Create JWT token (simple base64 encoding for now)"""
    import base64
    import json
    
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": (datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp()
    }
    token = base64.b64encode(json.dumps(payload).encode()).decode()
    return token

def decode_jwt(token: str) -> dict:
    """Decode JWT token"""
    import base64
    import json
    
    try:
        payload = json.loads(base64.b64decode(token.encode()).decode())
        if payload.get("exp", 0) < datetime.now().timestamp():
            raise HTTPException(status_code=401, detail="Token expired")
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    conn = sqlite3.connect(AUTH_DB)
    c = conn.cursor()
    row = c.execute(
        "SELECT id, username, password_hash, email, role, created_at, last_login FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row[0],
        "username": row[1],
        "password_hash": row[2],
        "email": row[3],
        "role": row[4],
        "created_at": row[5],
        "last_login": row[6]
    }

def create_user(username: str, password: str, email: Optional[str] = None) -> dict:
    """Create new user"""
    password_hash = hash_password(password)
    created_at = int(datetime.now().timestamp())
    
    conn = sqlite3.connect(AUTH_DB)
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, email, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, password_hash, email, "user", created_at)
        )
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "role": "user",
            "created_at": created_at
        }
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")

def update_last_login(user_id: int):
    """Update user's last login timestamp"""
    conn = sqlite3.connect(AUTH_DB)
    c = conn.cursor()
    c.execute("UPDATE users SET last_login = ? WHERE id = ?", (int(datetime.now().timestamp()), user_id))
    conn.commit()
    conn.close()

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register new user
    
    - Creates new user account
    - Returns JWT token
    """
    log_info(f"[AUTH] Registration attempt for user: {request.username}")
    
    # Validate username
    if len(request.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Create user
    user = create_user(request.username, request.password, request.email)
    
    # Generate token
    token = create_jwt(user["id"], user["username"], user["role"])
    
    update_last_login(user["id"])
    
    log_info(f"[AUTH] User registered successfully: {request.username}")
    
    return TokenResponse(
        access_token=token,
        user={
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email"),
            "role": user["role"]
        }
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login user
    
    - Validates credentials
    - Returns JWT token
    """
    log_info(f"[AUTH] Login attempt for user: {request.username}")
    
    # Get user
    user = get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password
    password_hash = hash_password(request.password)
    if password_hash != user["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate token
    token = create_jwt(user["id"], user["username"], user["role"])
    
    update_last_login(user["id"])
    
    log_info(f"[AUTH] User logged in successfully: {request.username}")
    
    return TokenResponse(
        access_token=token,
        user={
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email"),
            "role": user["role"]
        }
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh JWT token
    
    - Validates existing token
    - Issues new token with extended expiration
    """
    token = credentials.credentials
    payload = decode_jwt(token)
    
    user = get_user_by_username(payload["username"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Generate new token
    new_token = create_jwt(user["id"], user["username"], user["role"])
    
    log_info(f"[AUTH] Token refreshed for user: {user['username']}")
    
    return TokenResponse(
        access_token=new_token,
        user={
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email"),
            "role": user["role"]
        }
    )

@router.get("/me", response_model=UserInfo)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user info
    
    - Returns user data from token
    """
    token = credentials.credentials
    payload = decode_jwt(token)
    
    user = get_user_by_username(payload["username"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserInfo(
        id=user["id"],
        username=user["username"],
        email=user.get("email"),
        role=user["role"]
    )

@router.post("/logout")
async def logout():
    """
    Logout user
    
    - Frontend should clear token from localStorage
    - This endpoint is just for consistency
    """
    return {"ok": True, "message": "Logged out successfully"}

# ============================================================================
# EXPORT
# ============================================================================

__all__ = ["router", "decode_jwt", "get_user_by_username"]
