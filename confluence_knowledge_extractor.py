#!/usr/bin/env python3
"""
Confluence Knowledge Extractor - Refactored Version

Fetches articles from Confluence and saves to Supabase with improved modularity.
"""
import os
import sys
import json
import logging
import re
import requests
import html as html_module
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import quote

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('confluence-extractor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add backend to path for utilities
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)
    try:
        from app.utils.api_clients import ConfluenceAPIClient, SupabaseAPIClient
        from app.utils.text_processing import extract_text_from_html
        from app.utils.date_utils import parse_iso_date, format_date_for_storage
        from app.utils.ai_summarization import (
            call_openai_api,
            parse_json_response,
            format_summary_for_storage
        )
    except ImportError as e:
        logger.warning(f"Could not import from backend utils: {e}. Using inline implementations.")
        # Fallback: define utilities inline if imports fail
        class ConfluenceAPIClient:
            def __init__(self, url, email, api_token):
                self.base_url = url.rstrip('/')
                credentials = f"{email}:{api_token}"
                encoded = base64.b64encode(credentials.encode()).decode()
                self.headers = {
                    'Authorization': f'Basic {encoded}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            def call_api(self, endpoint, params=None):
                url = f"{self.base_url}/wiki/rest/api/{endpoint}"
                response = requests.get(url, headers=self.headers, params=params or {})
                response.raise_for_status()
                return response.json()
        
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
        
        def extract_text_from_html(html_content):
            text = re.sub(r'<[^>]+>', '', html_content)
            text = html_module.unescape(text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        
        def parse_iso_date(date_str):
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return datetime.now()
        
        def format_date_for_storage(date_obj):
            return date_obj.strftime('%Y-%m-%d')
        
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
            return "\n".join(parts)
else:
    logger.error("Backend directory not found. Please ensure backend/app/utils exists.")
    sys.exit(1)



class ConfluencePageExtractor:
    """Handles extraction of data from Confluence pages."""
    
    def __init__(self, confluence_client: ConfluenceAPIClient, space_key: str):
        """
        Initialize page extractor.
        
        Args:
            confluence_client: Confluence API client
            space_key: Confluence space key
        """
        self.confluence = confluence_client
        self.space_key = space_key
    
    def extract_page_data(self, page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract relevant data from a Confluence page.
        
        Args:
            page: Raw page data from Confluence API
            
        Returns:
            Extracted page data dictionary or None on error
        """
        try:
            page_id = page.get('id')
            title = page.get('title', 'Untitled')
            
            # Get page content
            body_storage = self._fetch_page_content(page_id)
            
            # Extract text content for AI processing
            text_content = extract_text_from_html(body_storage)
            
            # Generate initial summary
            summary = self._generate_initial_summary(text_content, title)
            
            # Build page URL
            page_url = self._build_page_url(page, page_id, title)
            
            # Extract metadata
            author = self._extract_author(page)
            version_info = self._extract_version_info(page)
            
            return {
                'id': page_id,
                'title': title,
                'summary': summary,
                'url': page_url,
                'author': author,
                'date': version_info['date'],
                'version': version_info['version'],
                'version_timestamp': version_info['timestamp'],
                'version_date': version_info['version_date'],
                'source': 'confluence',
                'raw_text': body_storage,
                'text_content': text_content
            }
        except Exception as e:
            logger.error(f"Error extracting data from page {page.get('id', 'unknown')}: {e}")
            return None
    
    def _fetch_page_content(self, page_id: str) -> str:
        """Fetch page content from Confluence API."""
        try:
            content_data = self.confluence.call_api(
                f'content/{page_id}?expand=body.storage,version,history'
            )
            return content_data.get('body', {}).get('storage', {}).get('value', '')
        except Exception as e:
            logger.warning(f"Could not fetch content for page {page_id}: {e}")
            return ''
    
    def _generate_initial_summary(self, text_content: str, title: str) -> str:
        """Generate initial summary from text content."""
        if text_content and len(text_content) > 200:
            return text_content[:200] + "..."
        elif text_content:
            return text_content
        else:
            return f"Confluence page: {title}"
    
    def _build_page_url(self, page: Dict[str, Any], page_id: str, title: str) -> str:
        """Build Confluence page URL."""
        space_key = page.get('space', {}).get('key', self.space_key)
        page_url = f"{self.confluence.base_url}/wiki{page.get('_links', {}).get('webui', '')}"
        
        if not page_url or page_url.endswith('/wiki'):
            # Fallback URL construction
            page_url = (
                f"{self.confluence.base_url}/wiki/spaces/{space_key}/"
                f"pages/{page_id}/{quote(title)}"
            )
        
        return page_url
    
    def _extract_author(self, page: Dict[str, Any]) -> str:
        """Extract author name from page data."""
        author_info = page.get('version', {}).get('by', {})
        return (
            author_info.get('displayName') or
            author_info.get('username') or
            'Unknown'
        )
    
    def _extract_version_info(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Extract version information from page data."""
        version_info = page.get('version', {})
        version_number = version_info.get('number', 1)
        version_date = version_info.get('when', '')
        
        if version_date:
            try:
                date_obj = parse_iso_date(version_date)
                date_str = format_date_for_storage(date_obj)
                version_timestamp = date_obj.timestamp()
            except Exception:
                date_obj = datetime.now()
                date_str = format_date_for_storage(date_obj)
                version_timestamp = date_obj.timestamp()
        else:
            date_obj = datetime.now()
            date_str = format_date_for_storage(date_obj)
            version_timestamp = date_obj.timestamp()
        
        return {
            'version': version_number,
            'version_date': version_date,
            'date': date_str,
            'timestamp': version_timestamp
        }


class ConfluenceAISummarizer:
    """Handles AI-powered summarization of Confluence articles."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize AI summarizer.
        
        Args:
            openai_api_key: OpenAI API key (optional)
        """
        self.api_key = openai_api_key
        self.enabled = bool(openai_api_key)
    
    def summarize_article(
        self,
        title: str,
        text_content: str
    ) -> Optional[Dict[str, Any]]:
        """
        Summarize a Confluence article using OpenAI.
        
        Args:
            title: Article title
            text_content: Plain text content
            
        Returns:
            Summary data dictionary or None if summarization fails
        """
        if not self.enabled:
            return None
        
        if not text_content or len(text_content.strip()) < 50:
            logger.debug(f"Skipping AI summarization for '{title}' - content too short")
            return None
        
        # Truncate content if too long
        max_length = 8000
        if len(text_content) > max_length:
            text_content = text_content[:max_length] + "..."
        
        prompt = self._build_summarization_prompt(title, text_content)
        system_message = (
            'You are a helpful assistant that analyzes Confluence articles '
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
        required_keys = ['summary', 'key_points']
        if not all(key in summary_data for key in required_keys):
            logger.warning("OpenAI response missing required keys")
            return None
        
        logger.info(f"Successfully generated AI summary for article: {title}")
        return summary_data
    
    def _build_summarization_prompt(self, title: str, text_content: str) -> str:
        """Build prompt for OpenAI summarization."""
        return f"""You are an AI assistant analyzing a Confluence article titled "{title}".

Analyze the following article content and provide a structured summary in JSON format with these exact keys:
- "summary": A concise 2-3 sentence summary of the main content
- "key_points": An array of 3-7 key points or important information from the article

Be specific and extract actual information from the article. Focus on the most important and actionable information.

Article Content:
{text_content}

Respond ONLY with valid JSON, no additional text or markdown formatting."""


class ConfluenceArticleManager:
    """Manages article storage and retrieval in Supabase."""
    
    def __init__(self, supabase_client: SupabaseAPIClient):
        """
        Initialize article manager.
        
        Args:
            supabase_client: Supabase API client
        """
        self.supabase = supabase_client
    
    def find_existing_article(self, page_id: str, page_url: str) -> Optional[Dict[str, Any]]:
        """
        Find existing article by Confluence page ID.
        
        Args:
            page_id: Confluence page ID
            page_url: Confluence page URL
            
        Returns:
            Existing article dictionary or None
        """
        params = {
            'select': 'id,raw_text,date,updated_at',
            'source': 'eq.confluence'
        }
        
        try:
            response = self.supabase.get('knowledge_items', params)
            if response.status_code != 200:
                return None
            
            items = response.json()
            for item in items:
                raw_text = item.get('raw_text', '')
                if raw_text.startswith('URL:'):
                    url_line = raw_text.split('\n')[0]
                    item_url = url_line.replace('URL:', '').strip()
                    if page_id in item_url or page_id in str(item.get('id', '')):
                        return item
        except Exception as e:
            logger.warning(f"Error checking for existing article: {e}")
        
        return None
    
    def extract_version_from_raw_text(self, raw_text: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """
        Extract version metadata from raw_text header.
        
        Returns:
            Tuple of (page_id, version, version_date)
        """
        page_id = None
        version = None
        version_date = None
        
        if not raw_text:
            return (page_id, version, version_date)
        
        lines = raw_text.split('\n')
        for line in lines[:10]:
            if line.startswith('CONFLUENCE_PAGE_ID:'):
                page_id = line.replace('CONFLUENCE_PAGE_ID:', '').strip()
            elif line.startswith('CONFLUENCE_VERSION:'):
                try:
                    version = int(line.replace('CONFLUENCE_VERSION:', '').strip())
                except (ValueError, AttributeError):
                    version = None
            elif line.startswith('CONFLUENCE_VERSION_DATE:'):
                version_date = line.replace('CONFLUENCE_VERSION_DATE:', '').strip()
        
        return (page_id, version, version_date)
    
    def build_raw_text_header(self, article_data: Dict[str, Any]) -> str:
        """Build metadata header for raw_text field."""
        parts = [
            f"URL: {article_data.get('url', '')}",
            f"CONFLUENCE_PAGE_TITLE: {article_data.get('title', '')}",
            f"CONFLUENCE_PAGE_ID: {article_data.get('id', '')}",
            f"CONFLUENCE_VERSION: {article_data.get('version', 1)}",
            f"CONFLUENCE_VERSION_DATE: {article_data.get('version_date', '')}",
            ""
        ]
        return "\n".join(parts)
    
    def insert_article(
        self,
        article_data: Dict[str, Any],
        summary_text: str,
        key_points: List[str]
    ) -> bool:
        """
        Insert new article into Supabase.
        
        Args:
            article_data: Article data dictionary
            summary_text: Formatted summary text
            key_points: List of key points
            
        Returns:
            True if successful, False otherwise
        """
        payload = {
            'summary': summary_text,
            'topics': [],
            'decisions': [],
            'key_points': key_points,
            'action_items': [],
            'faqs': [],
            'source': 'confluence',
            'date': article_data['date'],
            'project': article_data.get('project', ''),
            'sender_name': article_data['author'],
            'raw_text': self.build_raw_text_header(article_data) + article_data.get('raw_text', ''),
        }
        
        try:
            response = self.supabase.post('knowledge_items', payload)
            if response.status_code in (200, 201):
                logger.info(f"✅ Inserted article: {article_data['title']}")
                return True
            else:
                logger.error(f"Failed to insert article: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error inserting article: {e}")
            return False
    
    def update_article(
        self,
        article_id: str,
        article_data: Dict[str, Any],
        summary_text: str,
        key_points: List[str]
    ) -> bool:
        """
        Update existing article in Supabase.
        
        Args:
            article_id: Article ID
            article_data: Article data dictionary
            summary_text: Formatted summary text
            key_points: List of key points
            
        Returns:
            True if successful, False otherwise
        """
        payload = {
            'summary': summary_text,
            'date': article_data['date'],
            'sender_name': article_data['author'],
            'raw_text': self.build_raw_text_header(article_data) + article_data.get('raw_text', ''),
            'key_points': key_points,
            'decisions': [],
            'action_items': [],
        }
        
        try:
            response = self.supabase.patch('knowledge_items', article_id, payload)
            if response.status_code in (200, 204):
                logger.info(f"🔄 Updated article: {article_data['title']}")
                return True
            else:
                logger.error(f"Failed to update article: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error updating article: {e}")
            return False
    
    def should_update_article(
        self,
        existing: Dict[str, Any],
        current_data: Dict[str, Any]
    ) -> bool:
        """
        Determine if article should be updated based on version comparison.
        
        Args:
            existing: Existing article data
            current_data: Current article data
            
        Returns:
            True if update needed, False otherwise
        """
        existing_raw_text = existing.get('raw_text', '')
        existing_page_id, existing_version, existing_version_date = (
            self.extract_version_from_raw_text(existing_raw_text)
        )
        
        current_version = current_data.get('version', 1)
        current_version_date = current_data.get('version_date', '')
        
        # Compare versions
        if existing_version is not None and current_version is not None:
            if current_version > existing_version:
                logger.info(
                    f"Version changed: {existing_version} -> {current_version} "
                    f"for page {current_data.get('id')}"
                )
                return True
            elif current_version == existing_version and current_version_date != existing_version_date:
                logger.info(f"Version date changed for page {current_data.get('id')}")
                return True
        
        # Fallback: compare dates
        existing_date = existing.get('date', '')
        current_date = current_data.get('date', '')
        if current_date > existing_date:
            logger.info(f"Date changed: {existing_date} -> {current_date} for page {current_data.get('id')}")
            return True
        elif current_date == existing_date:
            # Check updated_at timestamp
            existing_updated = existing.get('updated_at', '')
            if existing_updated:
                try:
                    existing_updated_dt = parse_iso_date(existing_updated)
                    current_timestamp = current_data.get('version_timestamp', datetime.now().timestamp())
                    current_dt = datetime.fromtimestamp(current_timestamp)
                    if current_dt > existing_updated_dt:
                        logger.info(f"Content updated for page {current_data.get('id')}")
                        return True
                except Exception:
                    return True
        
        return False


class ConfluenceKnowledgeExtractor:
    """Main extractor class for Confluence knowledge extraction."""
    
    def __init__(self):
        """Initialize extractor with environment variables."""
        self._load_environment()
        self._validate_environment()
        self._initialize_clients()
        logger.info("ConfluenceKnowledgeExtractor initialized successfully")
        if self.ai_summarizer.enabled:
            logger.info("OpenAI API key found - AI summarization enabled")
        else:
            logger.warning("OpenAI API key not found - AI summarization disabled")
    
    def _load_environment(self):
        """Load environment variables."""
        self.confluence_url = os.getenv('CONFLUENCE_URL', '').rstrip('/')
        self.confluence_email = os.getenv('CONFLUENCE_EMAIL')
        self.confluence_api_token = os.getenv('CONFLUENCE_API_TOKEN')
        self.space_key = os.getenv('CONFLUENCE_SPACE_KEY')
        self.limit = int(os.getenv('CONFLUENCE_LIMIT', '50'))
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    def _validate_environment(self):
        """Validate required environment variables."""
        required = [
            'CONFLUENCE_URL',
            'CONFLUENCE_EMAIL',
            'CONFLUENCE_API_TOKEN',
            'CONFLUENCE_SPACE_KEY',
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY'
        ]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            logger.error(f"Missing required environment variables: {missing}")
            self._print_setup_instructions()
            sys.exit(1)
    
    def _print_setup_instructions(self):
        """Print setup instructions for missing environment variables."""
        logger.error("\nPlease set the following in your .env file:")
        logger.error("  CONFLUENCE_URL=https://your-domain.atlassian.net")
        logger.error("  CONFLUENCE_EMAIL=your-email@example.com")
        logger.error("  CONFLUENCE_API_TOKEN=your-api-token")
        logger.error("  CONFLUENCE_SPACE_KEY=SPACEKEY")
        logger.error("  SUPABASE_URL=your-supabase-url")
        logger.error("  SUPABASE_ANON_KEY=your-supabase-key")
    
    def _initialize_clients(self):
        """Initialize API clients."""
        self.confluence_client = ConfluenceAPIClient(
            self.confluence_url,
            self.confluence_email,
            self.confluence_api_token
        )
        self.supabase_client = SupabaseAPIClient(self.supabase_url, self.supabase_key)
        self.page_extractor = ConfluencePageExtractor(self.confluence_client, self.space_key)
        self.ai_summarizer = ConfluenceAISummarizer(self.openai_api_key)
        self.article_manager = ConfluenceArticleManager(self.supabase_client)
    
    def fetch_confluence_pages(self) -> List[Dict[str, Any]]:
        """Fetch pages from the specified Confluence space."""
        logger.info(f"Fetching pages from Confluence space: {self.space_key}")
        
        all_pages = []
        start = 0
        limit = min(self.limit, 50)  # Confluence API limit
        
        while len(all_pages) < self.limit:
            params = {
                'spaceKey': self.space_key,
                'limit': limit,
                'start': start,
                'expand': 'version,history,space'
            }
            
            try:
                data = self.confluence_client.call_api('content', params)
                pages = data.get('results', [])
                
                if not pages:
                    break
                
                all_pages.extend(pages)
                logger.info(f"Fetched {len(pages)} pages (total: {len(all_pages)})")
                
                # Check if there are more pages
                if len(all_pages) >= data.get('size', 0) or not data.get('_links', {}).get('next'):
                    break
                
                start += limit
            except Exception as e:
                logger.error(f"Error fetching pages: {e}")
                break
        
        logger.info(f"Total pages fetched: {len(all_pages)}")
        return all_pages[:self.limit]
    
    def _generate_summary_data(
        self,
        article_data: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """
        Generate summary and key points for article.
        
        Returns:
            Tuple of (summary_text, key_points)
        """
        summary_text = article_data.get('title', '')
        key_points = []
        
        if self.ai_summarizer.enabled and article_data.get('text_content'):
            summary_data = self.ai_summarizer.summarize_article(
                article_data.get('title', ''),
                article_data.get('text_content', '')
            )
            if summary_data:
                summary_text = format_summary_for_storage(summary_data)
                key_points = summary_data.get('key_points', [])
                logger.info(f"Generated AI summary for article: {article_data.get('title', '')}")
        
        return (summary_text, key_points)
    
    def save_article(self, article_data: Dict[str, Any]) -> bool:
        """
        Save article to Supabase (insert or update).
        
        Args:
            article_data: Article data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        page_id = article_data.get('id')
        if not page_id:
            logger.error("Article data missing page ID")
            return False
        
        page_url = article_data.get('url', '')
        existing = self.article_manager.find_existing_article(page_id, page_url)
        
        # Generate summary
        summary_text, key_points = self._generate_summary_data(article_data)
        
        if existing:
            if self.article_manager.should_update_article(existing, article_data):
                return self.article_manager.update_article(
                    existing['id'],
                    article_data,
                    summary_text,
                    key_points
                )
            else:
                logger.info(
                    f"⏭️  Skipping page {page_id} ({article_data.get('title', 'Unknown')}) - "
                    "no changes detected"
                )
                return True  # Not an error, just no update needed
        else:
            # Set project from space_key
            article_data['project'] = self.space_key
            return self.article_manager.insert_article(
                article_data,
                summary_text,
                key_points
            )
    
    def run_extraction_workflow(self) -> bool:
        """Execute the complete extraction workflow."""
        try:
            logger.info("=" * 60)
            logger.info("Starting Confluence Knowledge Extraction Workflow")
            logger.info("=" * 60)
            
            # Fetch pages
            pages = self.fetch_confluence_pages()
            if not pages:
                logger.warning("No pages found in Confluence space")
                return True
            
            # Process each page
            stats = {
                'processed': 0,
                'inserted': 0,
                'updated': 0,
                'skipped': 0,
                'errors': 0
            }
            
            for page in pages:
                stats['processed'] += 1
                
                article_data = self.page_extractor.extract_page_data(page)
                if not article_data:
                    stats['errors'] += 1
                    continue
                
                page_id = article_data.get('id', '')
                page_url = article_data.get('url', '')
                existing = self.article_manager.find_existing_article(page_id, page_url)
                
                success = self.save_article(article_data)
                if success:
                    if not existing:
                        stats['inserted'] += 1
                    else:
                        # Check if it was updated or skipped
                        existing_raw_text = existing.get('raw_text', '')
                        existing_page_id, existing_version, existing_version_date = (
                            self.article_manager.extract_version_from_raw_text(existing_raw_text)
                        )
                        current_version = article_data.get('version', 1)
                        
                        if existing_version is not None and current_version is not None:
                            if current_version > existing_version:
                                stats['updated'] += 1
                            else:
                                stats['skipped'] += 1
                        else:
                            # Fallback: check dates
                            existing_date = existing.get('date', '')
                            current_date = article_data.get('date', '')
                            if current_date > existing_date:
                                stats['updated'] += 1
                            else:
                                stats['skipped'] += 1
                else:
                    stats['errors'] += 1
            
            # Log statistics
            logger.info("=" * 60)
            logger.info(f"✅ Extraction completed:")
            logger.info(f"   Processed: {stats['processed']} pages")
            logger.info(f"   Inserted: {stats['inserted']} new articles")
            logger.info(f"   Updated: {stats['updated']} existing articles")
            logger.info(f"   Skipped: {stats['skipped']} unchanged articles")
            logger.info(f"   Errors: {stats['errors']}")
            logger.info("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"Error in extraction workflow: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    """Main entry point for the script."""
    try:
        extractor = ConfluenceKnowledgeExtractor()
        success = extractor.run_extraction_workflow()
        
        if success:
            logger.info("Confluence extraction completed successfully")
            sys.exit(0)
        else:
            logger.error("Confluence extraction failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

