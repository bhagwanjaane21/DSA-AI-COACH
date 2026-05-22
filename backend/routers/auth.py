"""
Authentication Router — POST /auth/register, POST /auth/login

Handles user registration and login using Supabase Auth.
On successful registration, also creates a profile row in the users table.
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import get_supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Request body for user registration."""
    email: str
    password: str
    name: Optional[str] = None
    current_level: str = "Beginner"


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: str
    password: str


class AuthResponse(BaseModel):
    """Response returned after successful auth."""
    user_id: str
    email: str
    name: Optional[str] = None
    access_token: str
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Register a new user.
    
    Flow:
        1. Create user in Supabase Auth (handles password hashing, email validation)
        2. Create a profile row in the 'users' table with their initial level
        3. Return the access token for immediate frontend use
    """
    db = get_supabase()

    try:
        # Step 1: Register with Supabase Auth
        auth_response = db.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=400,
                detail="Registration failed. Email may already be in use."
            )

        user_id = auth_response.user.id
        access_token = auth_response.session.access_token if auth_response.session else ""

        # Step 2: Create profile in users table
        db.table("users").insert({
            "id": user_id,
            "email": request.email,
            "name": request.name or request.email.split("@")[0],
            "current_level": request.current_level,
            "weak_topics": [],
        }).execute()

        # Step 3: Create empty learning_insights row for this user
        db.table("learning_insights").insert({
            "user_id": user_id,
            "weak_topics": [],
            "improvement_trends": {},
            "revision_history": [],
        }).execute()

        return AuthResponse(
            user_id=user_id,
            email=request.email,
            name=request.name,
            access_token=access_token,
            message="Registration successful! Welcome to DSA Coach.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login an existing user.
    
    Flow:
        1. Authenticate with Supabase Auth (validates email + password)
        2. Fetch the user's profile from the users table
        3. Return the access token for frontend session management
    """
    db = get_supabase()

    try:
        # Step 1: Sign in with Supabase Auth
        auth_response = db.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password."
            )

        user_id = auth_response.user.id
        access_token = auth_response.session.access_token if auth_response.session else ""

        # Step 2: Fetch user profile
        profile = db.table("users").select("name").eq("id", user_id).execute()
        name = profile.data[0]["name"] if profile.data else None

        return AuthResponse(
            user_id=user_id,
            email=request.email,
            name=name,
            access_token=access_token,
            message="Login successful!",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


# ---------------------------------------------------------------------------
# JWT Verification Helper (used as a dependency by other routers)
# ---------------------------------------------------------------------------

async def get_current_user(authorization: str = Header(..., description="Bearer <access_token>")):
    """
    FastAPI dependency to extract and verify the current user from JWT.
    
    Usage in other routers:
        @router.get("/protected-route")
        async def my_route(user = Depends(get_current_user)):
            user_id = user["id"]
    """
    db = get_supabase()

    try:
        # Extract token from "Bearer <token>" header
        token = authorization.replace("Bearer ", "").strip()

        # Verify with Supabase Auth
        user_response = db.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token.")

        return {
            "id": user_response.user.id,
            "email": user_response.user.email,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
