"""Pydantic models for request/response validation."""
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any


class ExportRequest(BaseModel):
    """Request model for exporting knowledge items."""
    filename: str
    format: str  # 'pdf' or 'csv'
    items: List[Dict[str, Any]]


class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""
    email: EmailStr
    password: str
    full_name: str
    role: str  # 'admin', 'project_lead', or 'team_member'


class SignUpRequest(BaseModel):
    """Request model for user signup."""
    email: EmailStr
    password: str
    full_name: str


class UpdateUserRoleRequest(BaseModel):
    """Request model for updating user role."""
    role: str  # 'admin', 'project_lead', or 'team_member'


class AIQuestionRequest(BaseModel):
    """Request model for AI Q&A."""
    question: str

