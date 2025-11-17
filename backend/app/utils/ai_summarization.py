"""AI summarization utilities using OpenAI API."""
import os
import json
import re
import logging
from typing import Dict, Any, Optional, List
import requests

logger = logging.getLogger(__name__)


def call_openai_api(
    prompt: str,
    system_message: str,
    model: str = 'gpt-4o-mini',
    temperature: float = 0.3,
    max_tokens: int = 1000,
    timeout: int = 30
) -> Optional[str]:
    """
    Call OpenAI API with a prompt and return the response content.
    
    Args:
        prompt: User prompt text
        system_message: System message for context
        model: OpenAI model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        timeout: Request timeout in seconds
        
    Returns:
        Response content string or None if request fails
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OPENAI_API_KEY not set, skipping AI summarization")
        return None
    
    logger.debug(f"Calling OpenAI API with key: {api_key[:20]}...")
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=timeout
        )
        
        if response.status_code != 200:
            error_detail = response.text
            logger.error(f"OpenAI API error: {response.status_code} - {error_detail}")
            # Log more details for debugging
            if response.status_code == 401:
                logger.error("OpenAI API authentication failed - check your API key")
            elif response.status_code == 429:
                logger.error("OpenAI API rate limit exceeded")
            return None
        
        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        return content if content else None
        
    except requests.exceptions.Timeout:
        logger.error("OpenAI API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI API request error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}", exc_info=True)
        return None


def parse_json_response(content: str) -> Optional[Dict[str, Any]]:
    """Parse JSON response from OpenAI, handling markdown code blocks."""
    try:
        # Remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.debug(f"Response content: {content}")
        return None


def format_summary_for_storage(summary_data: Dict[str, Any]) -> str:
    """
    Format AI-generated summary data into a readable markdown format for storage.
    
    Args:
        summary_data: Dictionary with keys: summary, key_points, decisions, action_items
        
    Returns:
        Formatted markdown string
    """
    parts = []
    
    # Summary section
    parts.append("## Summary")
    parts.append(summary_data.get('summary', 'No summary available.'))
    parts.append("")
    
    # Key Points section
    key_points = summary_data.get('key_points', [])
    if key_points:
        parts.append("## Key Points")
        for i, point in enumerate(key_points, 1):
            parts.append(f"{i}. {point}")
        parts.append("")
    
    # Decisions section (for Slack)
    decisions = summary_data.get('decisions', [])
    if decisions:
        parts.append("## Decisions")
        for i, decision in enumerate(decisions, 1):
            parts.append(f"{i}. {decision}")
        parts.append("")
    
    # Action Items section (for Slack)
    action_items = summary_data.get('action_items', [])
    if action_items:
        parts.append("## Action Items")
        for i, action in enumerate(action_items, 1):
            parts.append(f"{i}. {action}")
        parts.append("")
    
    return "\n".join(parts)

