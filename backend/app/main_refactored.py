"""FastAPI application main entry point."""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from supabase import create_client, Client
from dotenv import load_dotenv

from app.models import (
    ExportRequest,
    CreateUserRequest,
    SignUpRequest,
    UpdateUserRoleRequest
)
from app.services.export_service import to_csv, to_pdf
from app.services.user_service import UserService
from app.auth import verify_admin

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Ignite Knowledge Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase Admin Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print(
        "WARNING: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. "
        "User management endpoints will not work."
    )

supabase_admin: Optional[Client] = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Initialize services
user_service = UserService(supabase_admin) if supabase_admin else None


# Dependency to get user service
def get_user_service() -> UserService:
    """Get user service instance."""
    if not user_service:
        raise HTTPException(
            status_code=500,
            detail="User service not configured"
        )
    return user_service


# Dependency to get supabase admin client
def get_supabase_admin() -> Client:
    """Get Supabase admin client."""
    if not supabase_admin:
        raise HTTPException(
            status_code=500,
            detail="Supabase admin client not configured"
        )
    return supabase_admin


# ============================================================================
# Health and Root Endpoints
# ============================================================================

@app.get("/")
def root():
    """Redirect to interactive API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"ok": True}


# ============================================================================
# Export Endpoints
# ============================================================================

@app.post("/export")
def export_items(request: ExportRequest):
    """
    Export knowledge items to CSV or PDF format.
    
    Args:
        request: Export request with items and format
        
    Returns:
        Export file data with filename and MIME type
    """
    if request.format not in {"pdf", "csv"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Must be 'pdf' or 'csv'"
        )
    
    if request.format == "csv":
        csv_body = to_csv(request.items)
        filename = (
            request.filename
            if request.filename.endswith(".csv")
            else f"{request.filename}.csv"
        )
        return {
            "filename": filename,
            "mime": "text/csv",
            "body": csv_body,
        }
    
    # PDF format
    pdf_data = to_pdf(request.items)
    filename = (
        request.filename
        if request.filename.endswith(".pdf")
        else f"{request.filename}.pdf"
    )
    return {
        "filename": filename,
        "mime": "application/pdf",
        "body_b64": pdf_data.hex(),
    }


# ============================================================================
# Public Signup Endpoint
# ============================================================================

@app.post("/api/auth/signup")
async def signup(request: SignUpRequest):
    """
    Create a new user account with email already confirmed.
    
    Args:
        request: Signup request with email, password, and full name
        
    Returns:
        Created user information
    """
    supabase = get_supabase_admin()
    
    try:
        # Create user with email already confirmed using admin API
        response = supabase.auth.admin.create_user({
            "email": request.email,
            "password": request.password,
            "email_confirm": True,  # Bypass email confirmation
            "user_metadata": {
                "full_name": request.full_name,
                "role": "team_member",  # Default role for new signups
            }
        })
        
        return {
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": request.full_name,
                "email_confirmed_at": response.user.email_confirmed_at,
            },
            "message": "Account created successfully. You can now sign in."
        }
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists. Please sign in instead."
            )
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create account: {error_msg}"
        )


# ============================================================================
# User Management Endpoints (Admin Only)
# ============================================================================

async def get_current_admin(authorization: Optional[str] = Header(None)):
    """Dependency to get current admin user."""
    return await verify_admin(authorization, supabase_admin)


@app.get("/api/admin/users")
async def list_users(
    current_user=Depends(get_current_admin),
    service: UserService = Depends(get_user_service)
):
    """List all users (Admin only)."""
    try:
        users = service.list_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list users: {str(e)}"
        )


@app.post("/api/admin/users")
async def create_user(
    request: CreateUserRequest,
    current_user=Depends(get_current_admin),
    service: UserService = Depends(get_user_service)
):
    """Create a new user (Admin only)."""
    try:
        return service.create_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create user: {str(e)}"
        )


@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user=Depends(get_current_admin),
    service: UserService = Depends(get_user_service)
):
    """Delete a user (Admin only)."""
    try:
        service.delete_user(user_id)
        return {"success": True, "message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete user: {str(e)}"
        )


@app.patch("/api/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    current_user=Depends(get_current_admin),
    service: UserService = Depends(get_user_service)
):
    """Update user role (Admin only)."""
    try:
        return service.update_user_role(user_id, request.role)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update user role: {str(e)}"
        )


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

