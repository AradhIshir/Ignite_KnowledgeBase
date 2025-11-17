#!/usr/bin/env python3
"""
Slack Knowledge Extractor - Refactored Version

Extracts and consolidates Slack messages by keywords with improved modularity.
"""
import os
import sys
import json
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass

import requests

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slack-knowledge-extractor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add backend to path for utilities
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)
    try:
        from app.utils.api_clients import SlackAPIClient, SupabaseAPIClient
        from app.utils.text_processing import (
            normalize_text,
            clean_slack_message,
            singularize_keyword,
            hash_content,
            get_preview_text
        )
        from app.utils.date_utils import format_date_readable, format_date_for_storage
        from app.utils.ai_summarization import (
            call_openai_api,
            parse_json_response,
            format_summary_for_storage
        )
    except ImportError as e:
        logger.warning(f"Could not import from backend utils: {e}. Using inline implementations.")
        # Fallback implementations (simplified)
        import hashlib
        
        def normalize_text(text: str) -> str:
            text = text.replace('`', ' ').replace('*', ' ').replace('_', ' ').replace('~', ' ')
            text = re.sub(r"\s+", " ", text)
            return text.strip().lower()
        
        def clean_slack_message(text: str) -> str:
            text = re.sub(r'<!here>', '', text, flags=re.IGNORECASE)
            text = re.sub(r'<!channel>', '', text, flags=re.IGNORECASE)
            text = re.sub(r'<!everyone>', '', text, flags=re.IGNORECASE)
            text = re.sub(r'<@[A-Z0-9]+>', '', text)
            text = re.sub(r'<[^>]+\|[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        
        def singularize_keyword(keyword: str) -> str:
            if not keyword or not keyword.strip():
                return keyword
            keyword = keyword.strip()
            if len(keyword) > 3 and keyword.endswith('ies'):
                return keyword[:-3] + 'y'
            elif len(keyword) > 2 and keyword.endswith('es'):
                return keyword[:-2]
            elif len(keyword) > 1 and keyword.endswith('s'):
                return keyword[:-1]
            return keyword
        
        def hash_content(text: str) -> str:
            return hashlib.sha256(normalize_text(text).encode('utf-8')).hexdigest()
        
        def get_preview_text(text: str, max_words: int = 3) -> str:
            if not text:
                return ""
            words = text.strip().split()
            if len(words) >= max_words:
                return " ".join(words[:max_words]) + "..."
            elif words:
                return " ".join(words) + "..."
            return ""
        
        def format_date_readable(date_str: str) -> str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                return f"{date_obj.day} {date_obj.strftime('%b')}."
            except (ValueError, AttributeError):
                return date_str
        
        def format_date_for_storage(date_obj: datetime) -> str:
            return date_obj.strftime('%Y-%m-%d')
        
        class SlackAPIClient:
            def __init__(self, bot_token: str):
                self.bot_token = bot_token
                self.headers = {
                    'Authorization': f'Bearer {bot_token}',
                    'Content-Type': 'application/json'
                }
            def call_api(self, endpoint, params=None):
                url = f"https://slack.com/api/{endpoint}"
                response = requests.get(url, headers=self.headers, params=params or {})
                data = response.json()
                if not data.get('ok'):
                    raise RuntimeError(f"Slack API error: {data.get('error')}")
                return data
        
        class SupabaseAPIClient:
            def __init__(self, url, anon_key):
                self.base_url = url.rstrip('/')
                self.anon_key = anon_key
                self.headers = {
                    'apikey': anon_key,
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {anon_key}'
                }
            def get(self, table, params=None):
                url = f"{self.base_url}/rest/v1/{table}"
                return requests.get(url, headers=self.headers, params=params or {})
            def post(self, table, data):
                url = f"{self.base_url}/rest/v1/{table}"
                return requests.post(url, headers=self.headers, json=data)
            def patch(self, table, item_id, data):
                url = f"{self.base_url}/rest/v1/{table}"
                headers = {**self.headers, "Prefer": "return=representation"}
                return requests.patch(f"{url}?id=eq.{item_id}", headers=headers, json=data)
        
        def call_openai_api(prompt, system_message, model='gpt-4o-mini', temperature=0.3, max_tokens=1000, timeout=30):
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return None
            try:
                headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
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
                    return None
                return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            except Exception:
                return None
        
        def parse_json_response(content):
            try:
                content = re.sub(r'```json\s*', '', content)
                content = re.sub(r'```\s*', '', content)
                return json.loads(content.strip())
            except (json.JSONDecodeError, AttributeError):
                return None
        
        def format_summary_for_storage(summary_data):
            parts = ["## Summary", summary_data.get('summary', 'No summary available.'), ""]
            key_points = summary_data.get('key_points', [])
            if key_points:
                parts.append("## Key Points")
                for i, point in enumerate(key_points, 1):
                    parts.append(f"{i}. {point}")
                parts.append("")
            decisions = summary_data.get('decisions', [])
            if decisions:
                parts.append("## Decisions")
                for i, decision in enumerate(decisions, 1):
                    parts.append(f"{i}. {decision}")
                parts.append("")
            action_items = summary_data.get('action_items', [])
            if action_items:
                parts.append("## Action Items")
                for i, action in enumerate(action_items, 1):
                    parts.append(f"{i}. {action}")
                parts.append("")
            return "\n".join(parts)
else:
    logger.error("Backend directory not found. Please ensure backend/app/utils exists.")
    sys.exit(1)


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class SlackMessage:
    """Represents a Slack message with all relevant metadata."""
    text: str
    user: str
    channel: str
    timestamp: str
    thread_ts: Optional[str] = None
    files: Optional[List[Dict[str, Any]]] = None
    sender_name: Optional[str] = None
    is_thread_reply: bool = False
    original_thread_ts: Optional[str] = None


# ============================================================================
# Keyword Extraction
# ============================================================================

def read_file_safe(path: str) -> str:
    """Read file content safely, returning empty string on error."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Could not read {path}: {e}")
        return ""


def extract_keywords_from_readmes(frontend_path: str, backend_path: str) -> List[str]:
    """
    Extract keywords from frontend and backend README files.
    
    Args:
        frontend_path: Path to frontend README
        backend_path: Path to backend README
        
    Returns:
        List of extracted keywords
    """
    frontend_text = read_file_safe(frontend_path)
    backend_text = read_file_safe(backend_path)
    combined_text = f"{frontend_text}\n{backend_text}"
    
    candidates = set()
    
    # Extract bullet points (handles both "- keyword" and "-keyword" formats)
    bullet_items = re.findall(r"(?m)^\s*[-*]\s*(.+)$", combined_text)
    # Extract inline code blocks
    code_items = re.findall(r"`([^`]+)`", combined_text)
    
    for item in bullet_items + code_items:
        cleaned = normalize_text(item)
        cleaned = re.sub(r"[\s,:;.!?]+$", "", cleaned)
        
        # Skip empty or whitespace-only keywords
        if not cleaned or not cleaned.strip():
            continue
        
        # Keep only short phrases (4 words or less)
        if len(cleaned.split()) <= 4:
            candidates.add(cleaned)
    
    # Add known seeded keywords
    seeded_keywords = [
        'ui issues', 'dashboard', 'mia chatbot', 'recommendations', 'order history',
        'pending approvals', 'catalog', 'cart', 'authentication', 'rest api',
        'dental city webhook', 'mia chat api'
    ]
    for keyword in seeded_keywords:
        candidates.add(normalize_text(keyword))
    
    keywords = sorted(candidates)
    logger.info(f"Loaded {len(keywords)} keywords/phrases from README files")
    return keywords


# ============================================================================
# Keyword Matching
# ============================================================================

def find_matching_keywords(text: str, keywords: List[str]) -> Optional[Tuple[str, List[str]]]:
    """
    Find all matching keywords in text, prioritizing longer, more specific phrases.
    
    Args:
        text: Text to search
        keywords: List of keywords to match against
        
    Returns:
        Tuple of (best_match, all_matches) or None if no matches.
        Best match is the longest keyword (by word count, then character count).
    """
    normalized_text = normalize_text(text)
    matches = []
    
    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if not normalized_keyword:
            continue
        
        if ' ' in normalized_keyword:
            # Multi-word phrase: check if entire phrase is in text
            if normalized_keyword in normalized_text:
                matches.append(keyword)
        else:
            # Single word: check word boundary match
            if re.search(rf"\b{re.escape(normalized_keyword)}\b", normalized_text):
                matches.append(keyword)
    
    if not matches:
        return None
    
    # Sort by priority: word count (descending), then character length (descending)
    def priority(keyword: str) -> Tuple[int, int]:
        words = keyword.split()
        return (-len(words), -len(keyword))  # Negative for descending sort
    
    sorted_matches = sorted(matches, key=priority)
    return (sorted_matches[0], sorted_matches)


# ============================================================================
# OpenAI Summarization
# ============================================================================

def summarize_thread_with_openai(
    messages: List[SlackMessage],
    keyword: str
) -> Optional[Dict[str, Any]]:
    """
    Use OpenAI API to summarize a Slack conversation thread.
    
    Args:
        messages: List of Slack messages in the thread
        keyword: Topic keyword for context
        
    Returns:
        Dictionary with summary, key_points, decisions, action_items or None
    """
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logger.warning("OPENAI_API_KEY not set, skipping AI summarization")
        return None
    
    try:
        # Format messages for OpenAI
        conversation_text = "Slack Conversation Thread\n"
        conversation_text += f"Topic Keyword: {keyword}\n"
        conversation_text += "=" * 50 + "\n\n"
        
        for i, msg in enumerate(messages, 1):
            sender = msg.sender_name or f"User {msg.user}"
            msg_type = "Thread Reply" if msg.is_thread_reply else "Message"
            timestamp = datetime.fromtimestamp(float(msg.timestamp)).strftime("%Y-%m-%d %H:%M")
            conversation_text += f"[{msg_type}] {sender} ({timestamp}):\n{msg.text}\n\n"
        
        # Build prompt
        prompt = f"""You are an AI assistant analyzing a Slack conversation thread about "{keyword}".

Analyze the following conversation and provide a structured summary in JSON format with these exact keys:
- "summary": A concise 2-3 sentence summary of the main discussion
- "key_points": An array of 3-7 key points mentioned in the conversation
- "decisions": An array of any decisions made (can be empty if none)
- "action_items": An array of action items with assignees if mentioned (format: "Action: [description] - Assigned to: [person]" or just "Action: [description]" if no assignee)

Be specific and extract actual information from the conversation. If a section has no relevant content, use an empty array.

Conversation:
{conversation_text}

Respond ONLY with valid JSON, no additional text or markdown formatting."""

        system_message = (
            'You are a helpful assistant that analyzes Slack conversations '
            'and extracts structured information. Always respond with valid JSON only.'
        )
        
        content = call_openai_api(
            prompt=prompt,
            system_message=system_message,
            model='gpt-4o-mini',
            temperature=0.3,
            max_tokens=1000
        )
        
        if not content:
            return None
        
        summary_data = parse_json_response(content)
        if not summary_data:
            return None
        
        # Validate structure
        required_keys = ['summary', 'key_points', 'decisions', 'action_items']
        if not all(key in summary_data for key in required_keys):
            logger.warning("OpenAI response missing required keys")
            return None
        
        logger.info(f"Successfully generated AI summary for thread with {len(messages)} messages")
        return summary_data
        
    except Exception as e:
        logger.error(f"Error during OpenAI summarization: {str(e)}")
        return None


# ============================================================================
# Slack Message Processing
# ============================================================================

class SlackMessageProcessor:
    """Handles processing of Slack messages."""
    
    def __init__(self, slack_client: SlackAPIClient):
        """
        Initialize message processor.
        
        Args:
            slack_client: Slack API client
        """
        self.slack = slack_client
        self._user_cache: Dict[str, str] = {}
    
    def fetch_user_name(self, user_id: str) -> Optional[str]:
        """
        Fetch user's real name from Slack API (with caching).
        
        Args:
            user_id: Slack user ID
            
        Returns:
            User's display name or None
        """
        if not user_id or user_id == 'unknown':
            return None
        
        # Check cache first
        if user_id in self._user_cache:
            return self._user_cache[user_id]
        
        try:
            params = {'user': user_id}
            data = self.slack.call_api('users.info', params)
            user = data.get('user', {})
            name = (
                user.get('real_name') or
                user.get('profile', {}).get('display_name') or
                user.get('name', 'Unknown')
            )
            self._user_cache[user_id] = name
            return name
        except Exception:
            return None
    
    def process_message(
        self,
        msg: Dict[str, Any],
        channel_name: str
    ) -> Optional[SlackMessage]:
        """
        Convert raw Slack message to SlackMessage object.
        
        Args:
            msg: Raw message from Slack API
            channel_name: Channel name
            
        Returns:
            SlackMessage object or None if invalid
        """
        if msg.get('bot_id') or msg.get('subtype') or not msg.get('text'):
            return None
        
        msg_ts = msg['ts']
        thread_ts = msg.get('thread_ts')
        is_original = thread_ts is None or thread_ts == msg_ts
        
        user_id = msg.get('user', 'unknown')
        sender_name = self.fetch_user_name(user_id) if user_id != 'unknown' else None
        original_thread_ts = thread_ts if thread_ts and thread_ts != msg_ts else msg_ts
        
        return SlackMessage(
            text=clean_slack_message(msg['text']),
            user=user_id,
            channel=channel_name,
            timestamp=msg_ts,
            thread_ts=thread_ts,
            files=msg.get('files') or None,
            sender_name=sender_name,
            is_thread_reply=(thread_ts is not None and thread_ts != msg_ts),
            original_thread_ts=original_thread_ts
        )
    
    def process_thread_reply(
        self,
        reply: Dict[str, Any],
        channel_name: str,
        original_ts: str
    ) -> Optional[SlackMessage]:
        """
        Convert raw thread reply to SlackMessage object.
        
        Args:
            reply: Raw reply from Slack API
            channel_name: Channel name
            original_ts: Original thread timestamp
            
        Returns:
            SlackMessage object or None if invalid
        """
        if reply.get('bot_id') or reply.get('subtype') or not reply.get('text'):
            return None
        
        user_id = reply.get('user', 'unknown')
        sender_name = self.fetch_user_name(user_id) if user_id != 'unknown' else None
        
        return SlackMessage(
            text=clean_slack_message(reply['text']),
            user=user_id,
            channel=channel_name,
            timestamp=reply['ts'],
            thread_ts=original_ts,
            files=reply.get('files') or None,
            sender_name=sender_name,
            is_thread_reply=True,
            original_thread_ts=original_ts
        )


# ============================================================================
# Slack Article Manager
# ============================================================================

class SlackArticleManager:
    """Manages article storage and retrieval for Slack messages."""
    
    def __init__(self, supabase_client: SupabaseAPIClient):
        """
        Initialize article manager.
        
        Args:
            supabase_client: Supabase API client
        """
        self.supabase = supabase_client
    
    def find_existing_article(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Find existing knowledge article for keyword.
        
        Args:
            keyword: Topic keyword
            
        Returns:
            Existing article dictionary or None
        """
        topic_singular = singularize_keyword(keyword)
        params = {
            'select': 'id,raw_text,summary,topics,date',
            'source': 'eq.slack'
        }
        
        response = self.supabase.get('knowledge_items', params)
        if response.status_code != 200:
            return None
        
        items = response.json()
        for item in items:
            item_topics = item.get('topics', [])
            if isinstance(item_topics, list) and topic_singular in item_topics:
                return item
        
        return None
    
    def message_exists_in_article(self, content_hash: str, raw_text: str) -> bool:
        """
        Check if message hash already exists in article content.
        
        Args:
            content_hash: Message content hash
            raw_text: Article raw text
            
        Returns:
            True if message exists, False otherwise
        """
        return content_hash in str(raw_text)
    
    def format_message_for_storage(
        self,
        msg: SlackMessage,
        content_hash: str
    ) -> str:
        """
        Format message for storage with date and attachments.
        
        Args:
            msg: Slack message
            content_hash: Message content hash
            
        Returns:
            Formatted message string
        """
        message_type = "Thread Reply" if msg.is_thread_reply else "Message"
        msg_date = datetime.fromtimestamp(float(msg.timestamp))
        date_str = format_date_for_storage(msg_date)
        readable_date = format_date_readable(date_str)
        
        parts = [
            f"--- {message_type} from {msg.sender_name or 'Unknown'} on {readable_date} ---",
            f"Message: {msg.text}"
        ]
        
        # Add attachments if present
        if msg.files:
            attachments_json = []
            for file in msg.files:
                file_url = (
                    file.get('url_private') or
                    file.get('permalink') or
                    file.get('url', '')
                )
                if file_url:
                    attachments_json.append({
                        "name": file.get('name', 'Unknown'),
                        "url": file_url,
                        "type": file.get('mimetype', ''),
                        "size": file.get('size', 0)
                    })
            
            if attachments_json:
                parts.append(f"_attachments_json: {json.dumps(attachments_json)}")
                file_info = [f"{att['name']}: {att['url']}" for att in attachments_json]
                parts.append(f"Attachments: {'; '.join(file_info)}")
        
        parts.append(f"_msg_hash: {content_hash}")
        return "\n".join(parts)
    
    def append_to_existing_article(
        self,
        article: Dict[str, Any],
        msg: SlackMessage,
        content_hash: str
    ) -> Tuple[bool, str]:
        """
        Append message to existing article.
        
        Args:
            article: Existing article dictionary
            msg: Message to append
            content_hash: Message content hash
            
        Returns:
            Tuple of (success, action)
        """
        existing_text = article.get('raw_text', '')
        if self.message_exists_in_article(content_hash, existing_text):
            topic = singularize_keyword(article.get('topics', [''])[0])
            logger.info(f"Message already exists in {topic}, skipping")
            return (False, "duplicate")
        
        message_entry = self.format_message_for_storage(msg, content_hash)
        updated_text = existing_text + "\n\n" + message_entry
        
        update_payload = {"raw_text": updated_text}
        item_id = article['id']
        
        response = self.supabase.patch('knowledge_items', item_id, update_payload)
        
        if response.status_code in (200, 204):
            message_type = "reply" if msg.is_thread_reply else "message"
            topic = singularize_keyword(article.get('topics', [''])[0])
            logger.info(f"Appended {message_type} to existing page: {topic}")
            return (True, "updated")
        else:
            logger.error(f"Failed to update page: {response.status_code} {response.text}")
            return (False, "error")
    
    def create_new_article(
        self,
        topic_singular: str,
        msg: SlackMessage,
        content_hash: str,
        summary: str,
        decisions: List[str],
        key_points: List[str],
        action_items: List[str]
    ) -> Tuple[bool, str]:
        """
        Create new knowledge article for keyword.
        
        Args:
            topic_singular: Singularized topic keyword
            msg: Initial message
            content_hash: Message content hash
            summary: Article summary
            decisions: List of decisions
            key_points: List of key points
            action_items: List of action items
            
        Returns:
            Tuple of (success, action)
        """
        # Create article title
        keyword_words = [w for w in topic_singular.split() if w.strip()]
        if not keyword_words:
            logger.error(f"Topic '{topic_singular}' produced no words, skipping message {msg.timestamp}")
            return (False, "error")
        
        title = " ".join(word.capitalize() for word in keyword_words)
        
        message_entry = self.format_message_for_storage(msg, content_hash)
        msg_date = datetime.fromtimestamp(float(msg.timestamp))
        date_str = format_date_for_storage(msg_date)
        
        payload = {
            "summary": summary,
            "topics": [topic_singular],
            "decisions": decisions,
            "key_points": key_points,
            "action_items": action_items,
            "faqs": [],
            "source": "slack",
            "date": date_str,
            "project": msg.channel,
            "sender_name": msg.sender_name or "Unknown",
            "raw_text": message_entry
        }
        
        response = self.supabase.post('knowledge_items', payload)
        
        if response.status_code in (200, 201):
            logger.info(f"Created new page: {title}")
            return (True, "inserted")
        else:
            logger.error(f"Supabase insert failed: {response.status_code} {response.text}")
            return (False, "error")
    
    def update_article_summary_with_ai(
        self,
        article: Dict[str, Any],
        thread_messages: List[SlackMessage],
        keyword: str
    ) -> bool:
        """
        Update an existing article's summary with AI-generated summary.
        
        Args:
            article: Article dictionary
            thread_messages: List of thread messages
            keyword: Topic keyword
            
        Returns:
            True if successful, False otherwise
        """
        summary_data = summarize_thread_with_openai(thread_messages, keyword)
        if not summary_data:
            logger.warning(f"Failed to generate AI summary for article {article.get('id')}")
            return False
        
        # Format summary for storage
        formatted_summary = format_summary_for_storage(summary_data)
        
        # Update article with new summary
        item_id = article['id']
        update_payload = {"summary": formatted_summary}
        
        # Also update decisions, key_points, and action_items if available
        decisions = summary_data.get('decisions', [])
        key_points = summary_data.get('key_points', [])
        action_items = summary_data.get('action_items', [])
        if decisions:
            update_payload["decisions"] = decisions
        if key_points:
            update_payload["key_points"] = key_points
        if action_items:
            update_payload["action_items"] = action_items
        
        response = self.supabase.patch('knowledge_items', item_id, update_payload)
        
        if response.status_code in (200, 204):
            logger.info(f"Updated article summary with AI-generated content for keyword: {keyword}")
            return True
        else:
            logger.error(f"Failed to update article summary: {response.status_code} {response.text}")
            return False


# ============================================================================
# Slack Knowledge Extractor
# ============================================================================

class SlackKnowledgeExtractor:
    """Main extractor class for Slack knowledge extraction."""
    
    def __init__(self):
        """Initialize extractor with environment variables."""
        self._load_environment()
        self._validate_environment()
        self._initialize_clients()
        logger.info("SlackKnowledgeExtractor initialized successfully")
        if self.openai_api_key:
            logger.info("OpenAI API key found - AI summarization enabled")
        else:
            logger.warning("OpenAI API key not found - AI summarization disabled")
    
    def _load_environment(self):
        """Load environment variables."""
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.include_channels = self._parse_channel_list(os.getenv('INCLUDE_CHANNELS', ''))
        self.hours_back = int(os.getenv('EXTRACTION_HOURS_BACK', '24'))
    
    def _validate_environment(self):
        """Validate required environment variables."""
        required = ['SLACK_BOT_TOKEN', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            logger.error(f"Missing required environment variables: {missing}")
            sys.exit(1)
    
    def _parse_channel_list(self, channels_str: str) -> List[str]:
        """Parse comma-separated channel list into lowercase list."""
        return [c.strip().lower() for c in channels_str.split(',') if c.strip()]
    
    def _initialize_clients(self):
        """Initialize API clients and processors."""
        self.slack_client = SlackAPIClient(self.slack_token)
        self.supabase_client = SupabaseAPIClient(self.supabase_url, self.supabase_key)
        self.message_processor = SlackMessageProcessor(self.slack_client)
        self.article_manager = SlackArticleManager(self.supabase_client)
    
    def _list_channels(self) -> List[Dict[str, Any]]:
        """List all Slack channels."""
        data = self.slack_client.call_api('conversations.list')
        return data.get('channels', [])
    
    def _select_channels(self) -> List[Tuple[str, str]]:
        """Select channels to process based on configuration."""
        all_channels = self._list_channels()
        selected = []
        
        for channel in all_channels:
            if channel.get('is_archived'):
                continue
            
            channel_name = channel.get('name', '').lower()
            if self.include_channels and channel_name not in self.include_channels:
                continue
            
            selected.append((channel['id'], channel['name']))
        
        return selected
    
    def _fetch_channel_history(
        self,
        channel_id: str,
        oldest_ts: str,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """Fetch message history from a Slack channel."""
        params = {'channel': channel_id, 'oldest': oldest_ts, 'limit': limit}
        data = self.slack_client.call_api('conversations.history', params)
        return data.get('messages', [])
    
    def _fetch_thread_replies(
        self,
        channel_id: str,
        thread_ts: str
    ) -> List[Dict[str, Any]]:
        """Fetch all replies to a thread (excluding the parent message)."""
        try:
            params = {'channel': channel_id, 'ts': thread_ts}
            data = self.slack_client.call_api('conversations.replies', params)
            messages = data.get('messages', [])
            # First message is the parent, rest are replies
            return messages[1:] if len(messages) > 1 else []
        except Exception as e:
            logger.warning(f"Failed to fetch thread replies for {thread_ts}: {e}")
            return []
    
    def fetch_slack_messages(self) -> List[SlackMessage]:
        """Fetch all Slack messages from selected channels within time window."""
        logger.info(f"Fetching Slack messages for last {self.hours_back} hours...")
        oldest_ts = str(int((datetime.now() - timedelta(hours=self.hours_back)).timestamp()))
        messages = []
        
        selected_channels = self._select_channels()
        if not selected_channels:
            logger.warning('No channels selected (set INCLUDE_CHANNELS)')
            return messages
        
        processed_timestamps: Set[str] = set()
        
        for channel_id, channel_name in selected_channels:
            logger.info(f"Fetching messages from channel: {channel_name}")
            
            try:
                history = self._fetch_channel_history(channel_id, oldest_ts)
            except Exception as e:
                logger.error(f"Failed to fetch history for #{channel_name}: {e}")
                continue
            
            # Track original messages that have threads
            threads_to_fetch = {}
            
            # Process messages from history
            for msg in history:
                slack_msg = self.message_processor.process_message(msg, channel_name)
                if not slack_msg:
                    continue
                
                # Skip duplicates
                if slack_msg.timestamp in processed_timestamps:
                    continue
                processed_timestamps.add(slack_msg.timestamp)
                
                # Track threads for later fetching
                if not slack_msg.is_thread_reply:
                    reply_count = msg.get('reply_count', 0)
                    if reply_count > 0:
                        threads_to_fetch[slack_msg.timestamp] = msg
                
                messages.append(slack_msg)
            
            # Fetch and process thread replies
            for original_ts, original_msg in threads_to_fetch.items():
                try:
                    replies = self._fetch_thread_replies(channel_id, original_ts)
                    logger.info(f"Found {len(replies)} replies for thread {original_ts}")
                    
                    for reply in replies:
                        reply_msg = self.message_processor.process_thread_reply(
                            reply,
                            channel_name,
                            original_ts
                        )
                        if not reply_msg or reply_msg.timestamp in processed_timestamps:
                            continue
                        
                        processed_timestamps.add(reply_msg.timestamp)
                        messages.append(reply_msg)
                except Exception as e:
                    logger.warning(f"Error fetching thread replies for {original_ts}: {e}")
        
        logger.info(f"Fetched {len(messages)} messages from Slack")
        return messages
    
    def _group_messages_by_thread(
        self,
        messages: List[SlackMessage]
    ) -> Dict[str, List[SlackMessage]]:
        """
        Group messages by thread.
        
        Args:
            messages: List of Slack messages
            
        Returns:
            Dictionary mapping thread_ts to list of messages
        """
        thread_groups: Dict[str, List[SlackMessage]] = {}
        
        for msg in messages:
            thread_id = msg.original_thread_ts or msg.timestamp
            
            if thread_id not in thread_groups:
                thread_groups[thread_id] = []
            thread_groups[thread_id].append(msg)
        
        # Sort messages within each thread by timestamp
        for thread_id in thread_groups:
            thread_groups[thread_id].sort(key=lambda m: float(m.timestamp))
        
        return thread_groups
    
    def _validate_keyword(self, keyword: str) -> Optional[str]:
        """
        Validate and normalize keyword.
        
        Args:
            keyword: Raw keyword
            
        Returns:
            Validated keyword or None if invalid
        """
        if not keyword or not keyword.strip():
            return None
        
        keyword = keyword.strip()
        topic_singular = singularize_keyword(keyword)
        
        if not topic_singular or not topic_singular.strip():
            logger.warning(f"Singularization produced empty keyword for '{keyword}', using original")
            topic_singular = keyword.strip()
        
        if not topic_singular or not topic_singular.strip():
            return None
        
        return topic_singular.strip()
    
    def _process_matched_message(
        self,
        keyword: str,
        msg: SlackMessage,
        thread_messages: Optional[List[SlackMessage]] = None
    ) -> Tuple[bool, str]:
        """
        Process a message that matches a keyword (insert or update article).
        
        Args:
            keyword: Matched keyword
            msg: Slack message
            thread_messages: Optional list of thread messages
            
        Returns:
            Tuple of (success, action)
        """
        topic_singular = self._validate_keyword(keyword)
        if not topic_singular:
            logger.error(f"Invalid keyword '{keyword}' for message {msg.timestamp}, skipping")
            return (False, "error")
        
        content_hash = hash_content(msg.text)
        existing_article = self.article_manager.find_existing_article(keyword)
        
        if existing_article:
            result = self.article_manager.append_to_existing_article(
                existing_article,
                msg,
                content_hash
            )
            # Update summary if we have thread messages and OpenAI
            if result[0] and thread_messages and self.openai_api_key:
                self.article_manager.update_article_summary_with_ai(
                    existing_article,
                    thread_messages,
                    keyword
                )
            return result
        else:
            # Create new article
            summary = get_preview_text(msg.text) or f"Slack messages about {topic_singular}"
            decisions = []
            key_points = []
            action_items = []
            
            # Generate AI summary if available
            if thread_messages and self.openai_api_key and len(thread_messages) > 0:
                summary_data = summarize_thread_with_openai(thread_messages, topic_singular)
                if summary_data:
                    summary = format_summary_for_storage(summary_data)
                    decisions = summary_data.get('decisions', [])
                    key_points = summary_data.get('key_points', [])
                    action_items = summary_data.get('action_items', [])
                    logger.info(f"Created article with AI-generated summary for keyword: {topic_singular}")
            
            return self.article_manager.create_new_article(
                topic_singular,
                msg,
                content_hash,
                summary,
                decisions,
                key_points,
                action_items
            )
    
    def run_extraction_workflow(self) -> bool:
        """Execute the complete extraction workflow."""
        try:
            logger.info("=" * 60)
            logger.info("Starting Slack Knowledge Extraction Workflow (keyword + dedup)")
            logger.info("=" * 60)
            
            # Load keywords
            repo_root = os.getcwd()
            frontend_readme = os.path.join(repo_root, 'frontend', 'README.md')
            backend_readme = os.path.join(repo_root, 'backend', 'README.md')
            keywords = extract_keywords_from_readmes(frontend_readme, backend_readme)
            
            if not keywords:
                logger.warning('No keywords found in README files; nothing to match')
                return True
            
            # Fetch messages
            messages = self.fetch_slack_messages()
            if not messages:
                logger.warning("No messages found to process")
                return True
            
            # Group messages by thread
            thread_groups = self._group_messages_by_thread(messages)
            logger.info(f"Grouped {len(messages)} messages into {len(thread_groups)} threads")
            
            # Process messages grouped by thread and keyword
            stats = {
                'scanned': 0,
                'inserted': 0,
                'updated': 0,
                'summarized': 0
            }
            processed_threads: Set[str] = set()
            
            for msg in messages:
                stats['scanned'] += 1
                
                match_result = find_matching_keywords(msg.text, keywords)
                if not match_result:
                    continue
                
                best_match, all_matches = match_result
                if not best_match or not best_match.strip():
                    logger.warning(f"Empty keyword returned from matcher for message {msg.timestamp}, skipping")
                    continue
                
                # Get thread ID for this message
                thread_id = msg.original_thread_ts or msg.timestamp
                thread_messages = thread_groups.get(thread_id, [msg])
                
                # Process this message with its thread context
                # Only process once per thread-keyword combination
                thread_key = f"{thread_id}:{best_match}"
                if thread_key in processed_threads:
                    continue
                processed_threads.add(thread_key)
                
                success, action = self._process_matched_message(best_match, msg, thread_messages)
                
                if success:
                    if action == "inserted":
                        stats['inserted'] += 1
                        if thread_messages and self.openai_api_key:
                            stats['summarized'] += 1
                    elif action == "updated":
                        stats['updated'] += 1
            
            logger.info(
                f"Scanned: {stats['scanned']} messages | "
                f"Created new pages: {stats['inserted']} | "
                f"Updated pages: {stats['updated']} | "
                f"AI summaries generated: {stats['summarized']}"
            )
            logger.info("=" * 60)
            logger.info("✅ Slack Knowledge Extraction Workflow Completed Successfully")
            logger.info("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"Error in extraction workflow: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point for the script."""
    try:
        extractor = SlackKnowledgeExtractor()
        success = extractor.run_extraction_workflow()
        
        if success:
            logger.info("Extraction completed successfully")
            sys.exit(0)
        else:
            logger.error("Extraction failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

