"""Authentication and authorization utilities."""
from typing import Optional
from fastapi import HTTPException, Header
from supabase import Client
import logging

logger = logging.getLogger(__name__)


async def verify_admin(
    authorization: Optional[str] = Header(None),
    supabase_client: Optional[Client] = None
):
    """
    Verify that the user is an admin.
    
    Args:
        authorization: Authorization header value
        supabase_client: Supabase admin client
        
    Returns:
        User object if admin
        
    Raises:
        HTTPException: If authentication/authorization fails
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    
    if not supabase_client:
        raise HTTPException(
            status_code=500,
            detail="Supabase admin client not configured"
        )
    
    try:
        # Use admin client to get user from token
        user_response = supabase_client.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        role = user_response.user.user_metadata.get("role")
        if role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        
        return user_response.user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )

