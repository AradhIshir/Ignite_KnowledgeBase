from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import orjson
from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from fastapi.responses import RedirectResponse
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ExportRequest(BaseModel):
    filename: str
    format: str  # 'pdf' or 'csv'
    items: list[dict]


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # 'admin', 'project_lead', or 'team_member'


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UpdateUserRoleRequest(BaseModel):
    role: str  # 'admin', 'project_lead', or 'team_member'


def to_csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    out = [",".join([str(h) for h in headers])]
    for row in rows:
        out.append(
            ",".join([str(row.get(h, "")).replace("\n", " ").replace(",", ";") for h in headers])
        )
    return "\n".join(out)


app = FastAPI(title="Ignite Knowledge Backend")

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
    print("WARNING: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. User management endpoints will not work.")

supabase_admin: Optional[Client] = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


async def verify_admin(authorization: Optional[str] = Header(None)):
    """Verify that the user is an admin"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    # Verify token and check role using admin client (can verify any user's token)
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Supabase admin client not configured")
    
    try:
        # Use admin client to get user from token
        user_response = supabase_admin.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        role = user_response.user.user_metadata.get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return user_response.user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


@app.get("/")
def root():
    # Redirect to interactive docs for convenience
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/export")
def export_items(req: ExportRequest):
    if req.format not in {"pdf", "csv"}:
        raise HTTPException(status_code=400, detail="Unsupported format")

    if req.format == "csv":
        csv_body = to_csv(req.items)
        return {
            "filename": req.filename if req.filename.endswith(".csv") else f"{req.filename}.csv",
            "mime": "text/csv",
            "body": csv_body,
        }

    # PDF render via ReportLab (no system deps)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    def write_line(text: str, x: float, y: float, font_size: int = 11):
        c.setFont("Helvetica", font_size)
        c.drawString(x, y, text)
        return y

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.115, 0.455, 0.961)  # #1D74F5
    c.drawString(50, y, "Knowledge Export")
    c.setFillColorRGB(0, 0, 0)
    y -= 24

    for it in req.items:
        if y < 100:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica-Bold", 12)
        y = write_line(str(it.get("summary", "—")), 50, y)
        y -= 14
        meta = f"Project: {it.get('project','—')} | Source: {it.get('source','—')} | Date: {it.get('date','—')}"
        c.setFont("Helvetica", 10)
        y = write_line(meta, 50, y)
        y -= 10
        topics = it.get("topics") or []
        if topics:
            y = write_line("Topics: " + ", ".join(map(str, topics)), 50, y)
            y -= 12
        decisions = it.get("decisions") or []
        if decisions:
            y = write_line("Decisions:", 50, y)
            y -= 12
            for d in decisions:
                y = write_line(f"• {d}", 60, y)
                y -= 12
        faqs = it.get("faqs") or []
        if faqs:
            y = write_line("FAQs:", 50, y)
            y -= 12
            for f in faqs:
                y = write_line(f"• {f}", 60, y)
                y -= 12
        raw_text = it.get("raw_text")
        if raw_text:
            y = write_line("Original Content:", 50, y)
            y -= 12
            for line in str(raw_text).splitlines():
                if y < 80:
                    c.showPage()
                    y = height - 50
                y = write_line(line[:110], 60, y)
                y -= 12
        y -= 16

    c.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    return {
        "filename": req.filename if req.filename.endswith(".pdf") else f"{req.filename}.pdf",
        "mime": "application/pdf",
        "body_b64": pdf_data.hex(),
    }


# ============================================================================
# Public Signup Endpoint (No confirmation required)
# ============================================================================

@app.post("/api/auth/signup")
async def signup(req: SignUpRequest):
    """Create a new user account with email already confirmed (no confirmation needed)"""
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Supabase admin client not configured")
    
    try:
        # Create user with email already confirmed using admin API
        # This bypasses email confirmation requirement
        response = supabase_admin.auth.admin.create_user({
            "email": req.email,
            "password": req.password,
            "email_confirm": True,  # Email is already confirmed, no confirmation needed
            "user_metadata": {
                "full_name": req.full_name,
                "role": "team_member",  # Default role for new signups
            }
        })
        
        return {
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": req.full_name,
                "email_confirmed_at": response.user.email_confirmed_at,
            },
            "message": "Account created successfully. You can now sign in."
        }
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            raise HTTPException(status_code=400, detail="An account with this email already exists. Please sign in instead.")
        raise HTTPException(status_code=400, detail=f"Failed to create account: {error_msg}")


# ============================================================================
# User Management Endpoints (Admin Only)
# ============================================================================

@app.get("/api/admin/users")
async def list_users(current_user=Depends(verify_admin)):
    """List all users (Admin only)"""
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Supabase admin client not configured")
    
    try:
        # list_users() returns a list directly, not an object with .users
        response = supabase_admin.auth.admin.list_users()
        users = []
        
        # Handle both list response and object with .users attribute
        user_list = response if isinstance(response, list) else getattr(response, 'users', response)
        
        for user in user_list:
            # Handle both dict-like and object-like user objects
            user_id = user.id if hasattr(user, 'id') else user.get('id')
            user_email = user.email if hasattr(user, 'email') else user.get('email')
            user_metadata = user.user_metadata if hasattr(user, 'user_metadata') else user.get('user_metadata', {})
            user_created_at = user.created_at if hasattr(user, 'created_at') else user.get('created_at')
            
            role = user_metadata.get("role", "team_member") if isinstance(user_metadata, dict) else getattr(user_metadata, 'get', lambda k, d: d)("role", "team_member")
            full_name = user_metadata.get("full_name") if isinstance(user_metadata, dict) else getattr(user_metadata, 'get', lambda k: None)("full_name")
            
            users.append({
                "id": user_id,
                "email": user_email,
                "full_name": full_name,
                "role": role,
                "created_at": user_created_at,
            })
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")


@app.post("/api/admin/users")
async def create_user(req: CreateUserRequest, current_user=Depends(verify_admin)):
    """Create a new user (Admin only)"""
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Supabase admin client not configured")
    
    if req.role not in ["admin", "project_lead", "team_member"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be: admin, project_lead, or team_member")
    
    try:
        response = supabase_admin.auth.admin.create_user({
            "email": req.email,
            "password": req.password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": req.full_name,
                "role": req.role,
            }
        })
        
        return {
            "id": response.user.id,
            "email": response.user.email,
            "full_name": req.full_name,
            "role": req.role,
            "created_at": response.user.created_at,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")


@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: str, current_user=Depends(verify_admin)):
    """Delete a user (Admin only)"""
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Supabase admin client not configured")
    
    try:
        supabase_admin.auth.admin.delete_user(user_id)
        return {"success": True, "message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete user: {str(e)}")


@app.patch("/api/admin/users/{user_id}/role")
async def update_user_role(user_id: str, req: UpdateUserRoleRequest, current_user=Depends(verify_admin)):
    """Update user role (Admin only)"""
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Supabase admin client not configured")
    
    if req.role not in ["admin", "project_lead", "team_member"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be: admin, project_lead, or team_member")
    
    try:
        # Get current user to preserve existing metadata
        user_response = supabase_admin.auth.admin.get_user_by_id(user_id)
        current_metadata = user_response.user.user_metadata or {}
        
        # Update role while preserving other metadata
        current_metadata["role"] = req.role
        
        response = supabase_admin.auth.admin.update_user_by_id(
            user_id,
            {"user_metadata": current_metadata}
        )
        
        return {
            "id": response.user.id,
            "email": response.user.email,
            "role": req.role,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update user role: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

