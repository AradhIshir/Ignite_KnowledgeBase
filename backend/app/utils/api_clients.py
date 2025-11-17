"""API client utilities for external services."""
import os
import base64
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class ConfluenceAPIClient:
    """Client for Confluence REST API."""
    
    def __init__(self, url: str, email: str, api_token: str):
        """
        Initialize Confluence API client.
        
        Args:
            url: Confluence base URL
            email: Confluence account email
            api_token: Confluence API token
        """
        self.base_url = url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self._setup_headers()
    
    def _setup_headers(self):
        """Setup HTTP headers for Confluence API (Basic Auth)."""
        credentials = f"{self.email}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        self.headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def call_api(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a Confluence API call and return response data.
        
        Args:
            endpoint: API endpoint (e.g., 'content' or 'content/123')
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            requests.exceptions.RequestException: If API call fails
        """
        url = f"{self.base_url}/wiki/rest/api/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Confluence API error for {endpoint}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise


class SlackAPIClient:
    """Client for Slack Web API."""
    
    def __init__(self, bot_token: str):
        """
        Initialize Slack API client.
        
        Args:
            bot_token: Slack bot token
        """
        self.bot_token = bot_token
        self._setup_headers()
    
    def _setup_headers(self):
        """Setup HTTP headers for Slack API."""
        self.headers = {
            'Authorization': f'Bearer {self.bot_token}',
            'Content-Type': 'application/json'
        }
    
    def call_api(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a Slack API call and return response data.
        
        Args:
            endpoint: API endpoint (e.g., 'conversations.list')
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            RuntimeError: If API returns error
        """
        url = f"https://slack.com/api/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params or {})
        data = response.json()
        if not data.get('ok'):
            raise RuntimeError(f"Slack API error: {data.get('error')}")
        return data


class SupabaseAPIClient:
    """Client for Supabase REST API."""
    
    def __init__(self, url: str, anon_key: str):
        """
        Initialize Supabase API client.
        
        Args:
            url: Supabase project URL
            anon_key: Supabase anonymous key
        """
        self.base_url = url.rstrip('/')
        self.anon_key = anon_key
        self._setup_headers()
    
    def _setup_headers(self):
        """Setup HTTP headers for Supabase API."""
        self.headers = {
            'apikey': self.anon_key,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.anon_key}'
        }
    
    def get(self, table: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make GET request to Supabase table."""
        url = f"{self.base_url}/rest/v1/{table}"
        return requests.get(url, headers=self.headers, params=params or {})
    
    def post(self, table: str, data: Dict[str, Any]) -> requests.Response:
        """Make POST request to Supabase table."""
        url = f"{self.base_url}/rest/v1/{table}"
        return requests.post(url, headers=self.headers, json=data)
    
    def patch(self, table: str, item_id: str, data: Dict[str, Any]) -> requests.Response:
        """Make PATCH request to Supabase table."""
        url = f"{self.base_url}/rest/v1/{table}"
        headers = {**self.headers, "Prefer": "return=representation"}
        return requests.patch(
            f"{url}?id=eq.{item_id}",
            headers=headers,
            json=data
        )
    
    def delete(self, table: str, item_id: str) -> requests.Response:
        """Make DELETE request to Supabase table."""
        url = f"{self.base_url}/rest/v1/{table}"
        return requests.delete(f"{url}?id=eq.{item_id}", headers=self.headers)

