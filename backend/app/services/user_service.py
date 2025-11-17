"""Service for user management operations."""
from typing import List, Dict, Any, Optional
from supabase import Client
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing users via Supabase Admin API."""
    
    def __init__(self, supabase_client: Client):
        """
        Initialize user service.
        
        Args:
            supabase_client: Supabase admin client
        """
        self.supabase = supabase_client
    
    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users.
        
        Returns:
            List of user dictionaries
        """
        try:
            response = self.supabase.auth.admin.list_users()
            users = []
            
            # Handle both list response and object with .users attribute
            user_list = (
                response
                if isinstance(response, list)
                else getattr(response, 'users', response)
            )
            
            for user in user_list:
                # Handle both dict-like and object-like user objects
                user_id = user.id if hasattr(user, 'id') else user.get('id')
                user_email = user.email if hasattr(user, 'email') else user.get('email')
                user_metadata = (
                    user.user_metadata
                    if hasattr(user, 'user_metadata')
                    else user.get('user_metadata', {})
                )
                user_created_at = (
                    user.created_at
                    if hasattr(user, 'created_at')
                    else user.get('created_at')
                )
                
                role = (
                    user_metadata.get("role", "team_member")
                    if isinstance(user_metadata, dict)
                    else getattr(user_metadata, 'get', lambda k, d: d)("role", "team_member")
                )
                full_name = (
                    user_metadata.get("full_name")
                    if isinstance(user_metadata, dict)
                    else getattr(user_metadata, 'get', lambda k: None)("full_name")
                )
                
                users.append({
                    "id": user_id,
                    "email": user_email,
                    "full_name": full_name,
                    "role": role,
                    "created_at": user_created_at,
                })
            
            return users
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            raise
    
    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str = "team_member"
    ) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            email: User email
            password: User password
            full_name: User full name
            role: User role (default: team_member)
            
        Returns:
            Created user dictionary
        """
        if role not in ["admin", "project_lead", "team_member"]:
            raise ValueError(
                "Invalid role. Must be: admin, project_lead, or team_member"
            )
        
        try:
            response = self.supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": full_name,
                    "role": role,
                }
            })
            
            return {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": full_name,
                "role": role,
                "created_at": response.user.created_at,
            }
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def delete_user(self, user_id: str) -> None:
        """
        Delete a user.
        
        Args:
            user_id: User ID to delete
        """
        try:
            self.supabase.auth.admin.delete_user(user_id)
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise
    
    def update_user_role(self, user_id: str, role: str) -> Dict[str, Any]:
        """
        Update user role.
        
        Args:
            user_id: User ID
            role: New role
            
        Returns:
            Updated user dictionary
        """
        if role not in ["admin", "project_lead", "team_member"]:
            raise ValueError(
                "Invalid role. Must be: admin, project_lead, or team_member"
            )
        
        try:
            # Get current user to preserve existing metadata
            user_response = self.supabase.auth.admin.get_user_by_id(user_id)
            current_metadata = user_response.user.user_metadata or {}
            
            # Update role while preserving other metadata
            current_metadata["role"] = role
            
            response = self.supabase.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": current_metadata}
            )
            
            return {
                "id": response.user.id,
                "email": response.user.email,
                "role": role,
            }
        except Exception as e:
            logger.error(f"Failed to update user role: {e}")
            raise

