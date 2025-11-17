#!/usr/bin/env python3
"""
Slack Knowledge Extractor - Extracts and consolidates Slack messages by keywords.

Loads keywords from README files, fetches Slack messages, matches against keywords,
and consolidates all messages with the same keyword into a single knowledge article.
Uses OpenAI API to generate intelligent summaries of conversation threads.

Required environment variables:
- SLACK_BOT_TOKEN: Slack bot token for API access
- SUPABASE_URL: Supabase project URL
- SUPABASE_ANON_KEY: Supabase anonymous key
- OPENAI_API_KEY: OpenAI API key for thread summarization
- INCLUDE_CHANNELS (optional): Comma-separated channel names to include
- EXTRACTION_HOURS_BACK (optional): Hours to look back (default: 24)
"""
import os
import sys
import json
import logging
import requests
import re
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slack-knowledge-extractor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


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
# Text Processing Utilities
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for matching by removing formatting and lowercasing."""
    text = text.replace('`', ' ').replace('*', ' ').replace('_', ' ').replace('~', ' ')
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def clean_slack_message(text: str) -> str:
    """Remove Slack mention markup and clean whitespace."""
    # Remove special mentions
    text = re.sub(r'<!here>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<!channel>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<!everyone>', '', text, flags=re.IGNORECASE)
    # Remove user mentions
    text = re.sub(r'<@[A-Z0-9]+>', '', text)
    # Remove formatted links
    text = re.sub(r'<[^>]+\|[^>]+>', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def singularize_keyword(keyword: str) -> str:
    """Convert keyword to singular form for display."""
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


def format_date_readable(date_str: str) -> str:
    """Convert YYYY-MM-DD to readable format like '10 Nov.'"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_obj.day} {date_obj.strftime('%b')}."
    except Exception:
        return date_str


def get_preview_text(text: str) -> str:
    """Extract first three words for preview/description."""
    if not text:
        return ""
    words = text.strip().split()
    if len(words) >= 3:
        return " ".join(words[:3]) + "..."
    elif words:
        return " ".join(words) + "..."
    return ""


def hash_content(text: str) -> str:
    """Generate SHA256 hash of normalized text for deduplication."""
    return hashlib.sha256(normalize_text(text).encode('utf-8')).hexdigest()


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
    """Extract keywords from frontend and backend README files."""
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
        if not cleaned or not cleaned.strip() or len(cleaned.strip()) == 0:
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

def summarize_thread_with_openai(messages: List[SlackMessage], keyword: str) -> Optional[Dict[str, Any]]:
    """
    Use OpenAI API to summarize a Slack conversation thread.
    
    Returns a dictionary with:
    - summary: Concise summary of the discussion
    - key_points: List of key points mentioned
    - decisions: List of decisions made
    - action_items: List of action items assigned
    
    Returns None if summarization fails.
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
        
        # Create OpenAI API request
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

        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4o-mini',  # Using cost-effective model
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant that analyzes Slack conversations and extracts structured information. Always respond with valid JSON only.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 1000
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        if not content:
            logger.error("No content received from OpenAI API")
            return None
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()
            
            summary_data = json.loads(content)
            
            # Validate structure
            required_keys = ['summary', 'key_points', 'decisions', 'action_items']
            if not all(key in summary_data for key in required_keys):
                logger.warning("OpenAI response missing required keys, using fallback")
                return None
            
            logger.info(f"Successfully generated AI summary for thread with {len(messages)} messages")
            return summary_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            logger.debug(f"Response content: {content}")
            return None
            
    except Exception as e:
        logger.error(f"Error during OpenAI summarization: {str(e)}")
        return None


def format_ai_summary_for_storage(summary_data: Dict[str, Any]) -> str:
    """
    Format AI-generated summary data into a readable text format for storage.
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
    
    # Decisions section
    decisions = summary_data.get('decisions', [])
    if decisions:
        parts.append("## Decisions")
        for i, decision in enumerate(decisions, 1):
            parts.append(f"{i}. {decision}")
        parts.append("")
    
    # Action Items section
    action_items = summary_data.get('action_items', [])
    if action_items:
        parts.append("## Action Items")
        for i, action in enumerate(action_items, 1):
            parts.append(f"{i}. {action}")
        parts.append("")
    
    return "\n".join(parts)


# ============================================================================
# Slack Knowledge Extractor
# ============================================================================

class SlackKnowledgeExtractor:
    """Extracts and consolidates Slack messages into knowledge articles."""
    
    def __init__(self):
        """Initialize extractor with environment variables."""
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.include_channels = self._parse_channel_list(os.getenv('INCLUDE_CHANNELS', ''))
        self.hours_back = int(os.getenv('EXTRACTION_HOURS_BACK', '24'))
        
        self._validate_environment()
        self._setup_api_headers()
        logger.info("SlackKnowledgeExtractor initialized successfully")
        if self.openai_api_key:
            logger.info("OpenAI API key found - AI summarization enabled")
        else:
            logger.warning("OpenAI API key not found - AI summarization disabled")
    
    def _validate_environment(self):
        """Validate required environment variables."""
        required = ['SLACK_BOT_TOKEN', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            logger.error(f"Missing required environment variables: {missing}")
            sys.exit(1)
    
    def _setup_api_headers(self):
        """Setup HTTP headers for Slack and Supabase APIs."""
        self.slack_headers = {
            'Authorization': f'Bearer {self.slack_token}',
            'Content-Type': 'application/json'
        }
        self.supabase_headers = {
            'apikey': self.supabase_key,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.supabase_key}'
        }
    
    def _parse_channel_list(self, channels_str: str) -> List[str]:
        """Parse comma-separated channel list into lowercase list."""
        return [c.strip().lower() for c in channels_str.split(',') if c.strip()]
    
    # ========================================================================
    # Slack API Methods
    # ========================================================================
    
    def _call_slack_api(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a Slack API call and return response data."""
        url = f"https://slack.com/api/{endpoint}"
        response = requests.get(url, headers=self.slack_headers, params=params or {})
        data = response.json()
        if not data.get('ok'):
            raise RuntimeError(f"Slack API error: {data.get('error')}")
        return data
    
    def _list_channels(self) -> List[Dict[str, Any]]:
        """List all Slack channels."""
        data = self._call_slack_api('conversations.list')
        return data.get('channels', [])
    
    def _fetch_channel_history(self, channel_id: str, oldest_ts: str, limit: int = 200) -> List[Dict[str, Any]]:
        """Fetch message history from a Slack channel."""
        params = {'channel': channel_id, 'oldest': oldest_ts, 'limit': limit}
        data = self._call_slack_api('conversations.history', params)
        return data.get('messages', [])
    
    def _fetch_thread_replies(self, channel_id: str, thread_ts: str) -> List[Dict[str, Any]]:
        """Fetch all replies to a thread (excluding the parent message)."""
        try:
            params = {'channel': channel_id, 'ts': thread_ts}
            data = self._call_slack_api('conversations.replies', params)
            messages = data.get('messages', [])
            # First message is the parent, rest are replies
            return messages[1:] if len(messages) > 1 else []
        except Exception as e:
            logger.warning(f"Failed to fetch thread replies for {thread_ts}: {e}")
            return []
    
    def _fetch_user_name(self, user_id: str) -> Optional[str]:
        """Fetch user's real name from Slack API."""
        if not user_id or user_id == 'unknown':
            return None
        
        try:
            params = {'user': user_id}
            data = self._call_slack_api('users.info', params)
            user = data.get('user', {})
            return (user.get('real_name') or 
                   user.get('profile', {}).get('display_name') or 
                   user.get('name', 'Unknown'))
        except Exception:
            return None
    
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
    
    def _process_message(self, msg: Dict[str, Any], channel_name: str) -> Optional[SlackMessage]:
        """Convert raw Slack message to SlackMessage object."""
        if msg.get('bot_id') or msg.get('subtype') or not msg.get('text'):
            return None
        
        msg_ts = msg['ts']
        thread_ts = msg.get('thread_ts')
        is_original = thread_ts is None or thread_ts == msg_ts
        
        user_id = msg.get('user', 'unknown')
        sender_name = self._fetch_user_name(user_id) if user_id != 'unknown' else None
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
    
    def _process_thread_reply(self, reply: Dict[str, Any], channel_name: str, original_ts: str) -> Optional[SlackMessage]:
        """Convert raw thread reply to SlackMessage object."""
        if reply.get('bot_id') or reply.get('subtype') or not reply.get('text'):
            return None
        
        user_id = reply.get('user', 'unknown')
        sender_name = self._fetch_user_name(user_id) if user_id != 'unknown' else None
        
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
    
    def fetch_slack_messages(self) -> List[SlackMessage]:
        """Fetch all Slack messages from selected channels within time window."""
        logger.info(f"Fetching Slack messages for last {self.hours_back} hours...")
        oldest_ts = str(int((datetime.now() - timedelta(hours=self.hours_back)).timestamp()))
        messages = []
        
        selected_channels = self._select_channels()
        if not selected_channels:
            logger.warning('No channels selected (set INCLUDE_CHANNELS)')
            return messages
        
        processed_timestamps = set()
        
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
                slack_msg = self._process_message(msg, channel_name)
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
                        reply_msg = self._process_thread_reply(reply, channel_name, original_ts)
                        if not reply_msg or reply_msg.timestamp in processed_timestamps:
                            continue
                        
                        processed_timestamps.add(reply_msg.timestamp)
                        messages.append(reply_msg)
                except Exception as e:
                    logger.warning(f"Error fetching thread replies for {original_ts}: {e}")
        
        logger.info(f"Fetched {len(messages)} messages from Slack")
        return messages
    
    # ========================================================================
    # Supabase Methods
    # ========================================================================
    
    def _find_existing_article(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Find existing knowledge article for keyword (one article per keyword)."""
        topic_singular = singularize_keyword(keyword)
        params = {
            'select': 'id,raw_text,summary,topics,date',
            'source': 'eq.slack'
        }
        
        response = requests.get(
            f"{self.supabase_url}/rest/v1/knowledge_items",
            headers=self.supabase_headers,
            params=params
        )
        
        if response.status_code == 200:
            items = response.json()
            for item in items:
                item_topics = item.get('topics', [])
                if isinstance(item_topics, list) and topic_singular in item_topics:
                    return item
        
        return None
    
    def _message_exists_in_article(self, content_hash: str, raw_text: str) -> bool:
        """Check if message hash already exists in article content."""
        return content_hash in str(raw_text)
    
    def _format_message_for_storage(self, msg: SlackMessage, content_hash: str) -> str:
        """Format message for storage with date and attachments."""
        message_type = "Thread Reply" if msg.is_thread_reply else "Message"
        msg_date = datetime.fromtimestamp(float(msg.timestamp)).strftime("%Y-%m-%d")
        readable_date = format_date_readable(msg_date)
        
        parts = [
            f"--- {message_type} from {msg.sender_name or 'Unknown'} on {readable_date} ---",
            f"Message: {msg.text}"
        ]
        
        # Add attachments if present
        if msg.files:
            attachments_json = []
            for file in msg.files:
                file_url = file.get('url_private') or file.get('permalink') or file.get('url', '')
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
    
    def _validate_keyword(self, keyword: str) -> Optional[str]:
        """Validate and normalize keyword, returning None if invalid."""
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
    
    def _create_article_title(self, topic_singular: str) -> Optional[str]:
        """Create article title from keyword (keyword only, no date)."""
        keyword_words = [w for w in topic_singular.split() if w.strip()]
        if not keyword_words:
            return None
        return " ".join(word.capitalize() for word in keyword_words)
    
    def _group_messages_by_thread(self, messages: List[SlackMessage]) -> Dict[str, List[SlackMessage]]:
        """
        Group messages by thread. Messages without threads are grouped by their timestamp.
        Returns a dictionary mapping thread_ts to list of messages.
        """
        thread_groups: Dict[str, List[SlackMessage]] = {}
        
        for msg in messages:
            # Use original_thread_ts if available, otherwise use timestamp as thread identifier
            thread_id = msg.original_thread_ts or msg.timestamp
            
            if thread_id not in thread_groups:
                thread_groups[thread_id] = []
            thread_groups[thread_id].append(msg)
        
        # Sort messages within each thread by timestamp
        for thread_id in thread_groups:
            thread_groups[thread_id].sort(key=lambda m: float(m.timestamp))
        
        return thread_groups
    
    def _append_to_existing_article(self, article: Dict[str, Any], msg: SlackMessage, content_hash: str) -> Tuple[bool, str]:
        """Append message to existing article."""
        existing_text = article.get('raw_text', '')
        if self._message_exists_in_article(content_hash, existing_text):
            topic = singularize_keyword(article.get('topics', [''])[0])
            logger.info(f"Message already exists in {topic}, skipping")
            return (False, "duplicate")
        
        message_entry = self._format_message_for_storage(msg, content_hash)
        updated_text = existing_text + "\n\n" + message_entry
        
        update_payload = {"raw_text": updated_text}
        item_id = article['id']
        
        response = requests.patch(
            f"{self.supabase_url}/rest/v1/knowledge_items?id=eq.{item_id}",
            headers={**self.supabase_headers, "Prefer": "return=representation"},
            data=json.dumps(update_payload)
        )
        
        if response.status_code in (200, 204):
            message_type = "reply" if msg.is_thread_reply else "message"
            topic = singularize_keyword(article.get('topics', [''])[0])
            logger.info(f"Appended {message_type} to existing page: {topic}")
            return (True, "updated")
        else:
            logger.error(f"Failed to update page: {response.status_code} {response.text}")
            return (False, "error")
    
    def _update_article_summary_with_ai(self, article: Dict[str, Any], thread_messages: List[SlackMessage], keyword: str) -> bool:
        """
        Update an existing article's summary with AI-generated summary from thread messages.
        """
        if not self.openai_api_key:
            return False
        
        # Generate AI summary
        summary_data = summarize_thread_with_openai(thread_messages, keyword)
        if not summary_data:
            logger.warning(f"Failed to generate AI summary for article {article.get('id')}")
            return False
        
        # Format summary for storage
        formatted_summary = format_ai_summary_for_storage(summary_data)
        
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
        
        response = requests.patch(
            f"{self.supabase_url}/rest/v1/knowledge_items?id=eq.{item_id}",
            headers={**self.supabase_headers, "Prefer": "return=representation"},
            data=json.dumps(update_payload)
        )
        
        if response.status_code in (200, 204):
            logger.info(f"Updated article summary with AI-generated content for keyword: {keyword}")
            return True
        else:
            logger.error(f"Failed to update article summary: {response.status_code} {response.text}")
            return False
    
    def _create_new_article(self, topic_singular: str, msg: SlackMessage, content_hash: str, thread_messages: Optional[List[SlackMessage]] = None) -> Tuple[bool, str]:
        """Create new knowledge article for keyword."""
        title = self._create_article_title(topic_singular)
        if not title:
            logger.error(f"Topic '{topic_singular}' produced no words, skipping message {msg.timestamp}")
            return (False, "error")
        
        # Use AI summary if available, otherwise use preview text
        summary = get_preview_text(msg.text) or f"Slack messages about {topic_singular}"
        decisions = []
        key_points = []
        action_items = []
        
        # If we have thread messages and OpenAI key, generate AI summary
        if thread_messages and self.openai_api_key and len(thread_messages) > 0:
            summary_data = summarize_thread_with_openai(thread_messages, topic_singular)
            if summary_data:
                summary = format_ai_summary_for_storage(summary_data)
                decisions = summary_data.get('decisions', [])
                key_points = summary_data.get('key_points', [])
                action_items = summary_data.get('action_items', [])
                logger.info(f"Created article with AI-generated summary for keyword: {topic_singular}")
        
        message_entry = self._format_message_for_storage(msg, content_hash)
        msg_date = datetime.fromtimestamp(float(msg.timestamp)).strftime("%Y-%m-%d")
        
        payload = {
            "summary": summary,
            "topics": [topic_singular],
            "decisions": decisions,
            "key_points": key_points,
            "action_items": action_items,
            "faqs": [],  # Keep faqs separate from action_items
            "source": "slack",
            "date": msg_date,
            "project": msg.channel,
            "sender_name": msg.sender_name or "Unknown",
            "raw_text": message_entry
        }
        
        response = requests.post(
            f"{self.supabase_url}/rest/v1/knowledge_items",
            headers=self.supabase_headers,
            data=json.dumps(payload)
        )
        
        if response.status_code in (200, 201):
            logger.info(f"Created new page: {title}")
            return (True, "inserted")
        else:
            logger.error(f"Supabase insert failed: {response.status_code} {response.text}")
            return (False, "error")
    
    def _process_matched_message(self, keyword: str, msg: SlackMessage, thread_messages: Optional[List[SlackMessage]] = None) -> Tuple[bool, str]:
        """Process a message that matches a keyword (insert or update article)."""
        topic_singular = self._validate_keyword(keyword)
        if not topic_singular:
            logger.error(f"Invalid keyword '{keyword}' for message {msg.timestamp}, skipping")
            return (False, "error")
        
        content_hash = hash_content(msg.text)
        existing_article = self._find_existing_article(keyword)
        
        if existing_article:
            result = self._append_to_existing_article(existing_article, msg, content_hash)
            # If we have thread messages and this is a new thread being added, update summary
            if result[0] and thread_messages and self.openai_api_key:
                # Re-fetch all messages for this keyword to get complete thread
                # For now, we'll update summary when we have thread messages
                self._update_article_summary_with_ai(existing_article, thread_messages, keyword)
            return result
        else:
            return self._create_new_article(topic_singular, msg, content_hash, thread_messages)
    
    # ========================================================================
    # Main Workflow
    # ========================================================================
    
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
            stats = {'scanned': 0, 'inserted': 0, 'updated': 0, 'summarized': 0}
            processed_threads = set()
            
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
            
            logger.info(f"Scanned: {stats['scanned']} messages | "
                       f"Created new pages: {stats['inserted']} | "
                       f"Updated pages: {stats['updated']} | "
                       f"AI summaries generated: {stats['summarized']}")
            logger.info("=" * 60)
            logger.info("✅ Slack Knowledge Extraction Workflow Completed Successfully")
            logger.info("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"Error in extraction workflow: {str(e)}")
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
        sys.exit(1)


if __name__ == "__main__":
    main()
