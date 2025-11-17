#!/usr/bin/env python3
"""
Confluence Knowledge Extractor - Fetches articles from Confluence and saves to Supabase.

This script connects to Confluence Cloud REST API, fetches pages from a specified space,
and inserts/updates them in the Supabase knowledge_items table.

Required environment variables:
- CONFLUENCE_URL: Your Confluence Cloud URL (e.g., https://your-domain.atlassian.net)
- CONFLUENCE_EMAIL: Your Confluence account email
- CONFLUENCE_API_TOKEN: Confluence API token (generate from https://id.atlassian.com/manage-profile/security/api-tokens)
- CONFLUENCE_SPACE_KEY: Space key to fetch pages from (e.g., "PROJ" or "~username")
- SUPABASE_URL: Supabase project URL
- SUPABASE_ANON_KEY: Supabase anonymous key
- OPENAI_API_KEY: OpenAI API key for AI-powered summarization (optional)
- CONFLUENCE_LIMIT (optional): Maximum number of pages to fetch (default: 50)
"""
import os
import sys
import json
import logging
import requests
import re
import html as html_module
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('confluence-extractor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# Confluence Knowledge Extractor
# ============================================================================

class ConfluenceKnowledgeExtractor:
    """Extracts articles from Confluence and saves them to Supabase."""
    
    def __init__(self):
        """Initialize extractor with environment variables."""
        self.confluence_url = os.getenv('CONFLUENCE_URL', '').rstrip('/')
        self.confluence_email = os.getenv('CONFLUENCE_EMAIL')
        self.confluence_api_token = os.getenv('CONFLUENCE_API_TOKEN')
        self.space_key = os.getenv('CONFLUENCE_SPACE_KEY')
        self.limit = int(os.getenv('CONFLUENCE_LIMIT', '50'))
        
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        self._validate_environment()
        self._setup_api_headers()
        logger.info("ConfluenceKnowledgeExtractor initialized successfully")
        if self.openai_api_key:
            logger.info("OpenAI API key found - AI summarization enabled")
        else:
            logger.warning("OpenAI API key not found - AI summarization disabled")
    
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
            logger.error("\nPlease set the following in your .env file:")
            logger.error("  CONFLUENCE_URL=https://your-domain.atlassian.net")
            logger.error("  CONFLUENCE_EMAIL=your-email@example.com")
            logger.error("  CONFLUENCE_API_TOKEN=your-api-token")
            logger.error("  CONFLUENCE_SPACE_KEY=SPACEKEY")
            logger.error("  SUPABASE_URL=your-supabase-url")
            logger.error("  SUPABASE_ANON_KEY=your-supabase-key")
            sys.exit(1)
    
    def _setup_api_headers(self):
        """Setup HTTP headers for Confluence and Supabase APIs."""
        # Confluence uses Basic Auth with email:API_TOKEN
        import base64
        credentials = f"{self.confluence_email}:{self.confluence_api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        self.confluence_headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        self.supabase_headers = {
            'apikey': self.supabase_key,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.supabase_key}'
        }
    
    # ========================================================================
    # Confluence API Methods
    # ========================================================================
    
    def _call_confluence_api(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a Confluence API call and return response data."""
        url = f"{self.confluence_url}/wiki/rest/api/{endpoint}"
        try:
            response = requests.get(url, headers=self.confluence_headers, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Confluence API error for {endpoint}: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    def fetch_confluence_pages(self) -> List[Dict[str, Any]]:
        """Fetch pages from the specified Confluence space."""
        logger.info(f"Fetching pages from Confluence space: {self.space_key}")
        
        all_pages = []
        start = 0
        limit = min(self.limit, 50)  # Confluence API limit is 50 per request
        
        while len(all_pages) < self.limit:
            params = {
                'spaceKey': self.space_key,
                'limit': limit,
                'start': start,
                'expand': 'version,history,space'
            }
            
            try:
                data = self._call_confluence_api('content', params)
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
    
    def extract_page_data(self, page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract relevant data from a Confluence page."""
        try:
            page_id = page.get('id')
            title = page.get('title', 'Untitled')
            
            # Get page content (body)
            try:
                content_data = self._call_confluence_api(f'content/{page_id}?expand=body.storage,version,history')
                body_storage = content_data.get('body', {}).get('storage', {}).get('value', '')
            except Exception as e:
                logger.warning(f"Could not fetch content for page {page_id}: {e}")
                body_storage = ''
            
            # Extract text content from HTML for processing
            # Remove HTML tags
            text_content = re.sub(r'<[^>]+>', '', body_storage)
            # Decode HTML entities
            text_content = html_module.unescape(text_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Initial summary (will be replaced by AI if available)
            summary = text_content[:200] + "..." if len(text_content) > 200 else text_content
            if not summary:
                summary = f"Confluence page: {title}"
            
            # Get URL
            space_key = page.get('space', {}).get('key', self.space_key)
            page_url = f"{self.confluence_url}/wiki{page.get('_links', {}).get('webui', '')}"
            if not page_url or page_url.endswith('/wiki'):
                # Fallback URL construction
                page_url = f"{self.confluence_url}/wiki/spaces/{space_key}/pages/{page_id}/{quote(title)}"
            
            # Get author
            author_info = page.get('version', {}).get('by', {})
            author = author_info.get('displayName') or author_info.get('username') or 'Unknown'
            
            # Get version number and date
            version_info = page.get('version', {})
            version_number = version_info.get('number', 1)
            version_date = version_info.get('when', '')
            
            if version_date:
                try:
                    # Parse ISO format date
                    date_obj = datetime.fromisoformat(version_date.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d')
                    version_timestamp = date_obj.timestamp()
                except Exception:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    version_timestamp = datetime.now().timestamp()
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
                version_timestamp = datetime.now().timestamp()
            
            return {
                'id': page_id,
                'title': title,
                'summary': summary,
                'url': page_url,
                'author': author,
                'date': date_str,
                'version': version_number,
                'version_timestamp': version_timestamp,
                'version_date': version_date,
                'source': 'confluence',
                'raw_text': body_storage,  # Store full HTML content
                'text_content': text_content  # Store plain text for AI processing
            }
        except Exception as e:
            logger.error(f"Error extracting data from page {page.get('id', 'unknown')}: {e}")
            return None
    
    # ========================================================================
    # OpenAI Summarization Methods
    # ========================================================================
    
    def summarize_article_with_openai(self, title: str, text_content: str) -> Optional[Dict[str, Any]]:
        """
        Use OpenAI API to summarize a Confluence article.
        
        Returns a dictionary with:
        - summary: Concise summary of the article
        - key_points: List of key points mentioned
        
        Returns None if summarization fails.
        """
        if not self.openai_api_key:
            return None
        
        if not text_content or len(text_content.strip()) < 50:
            logger.debug(f"Skipping AI summarization for '{title}' - content too short")
            return None
        
        try:
            # Truncate content if too long (OpenAI has token limits)
            max_length = 8000  # Leave room for prompt and response
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "..."
            
            prompt = f"""You are an AI assistant analyzing a Confluence article titled "{title}".

Analyze the following article content and provide a structured summary in JSON format with these exact keys:
- "summary": A concise 2-3 sentence summary of the main content
- "key_points": An array of 3-7 key points or important information from the article

Be specific and extract actual information from the article. Focus on the most important and actionable information.

Article Content:
{text_content}

Respond ONLY with valid JSON, no additional text or markdown formatting."""

            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant that analyzes Confluence articles and extracts structured information. Always respond with valid JSON only.'
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
                required_keys = ['summary', 'key_points']
                if not all(key in summary_data for key in required_keys):
                    logger.warning("OpenAI response missing required keys, using fallback")
                    return None
                
                logger.info(f"Successfully generated AI summary for article: {title}")
                return summary_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI JSON response: {e}")
                logger.debug(f"Response content: {content}")
                return None
                
        except Exception as e:
            logger.error(f"Error during OpenAI summarization: {str(e)}")
            return None
    
    def format_ai_summary_for_storage(self, summary_data: Dict[str, Any]) -> str:
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
        
        return "\n".join(parts)
    
    # ========================================================================
    # Supabase Methods
    # ========================================================================
    
    def _find_existing_article(self, page_id: str, page_url: str) -> Optional[Dict[str, Any]]:
        """Find existing article in Supabase by checking Confluence page ID in URL."""
        # Get all Confluence articles and check for matching page ID in URL
        params = {
            'select': 'id,raw_text,date,updated_at',
            'source': 'eq.confluence'
        }
        
        try:
            response = requests.get(
                f"{self.supabase_url}/rest/v1/knowledge_items",
                headers=self.supabase_headers,
                params=params
            )
            
            if response.status_code == 200:
                items = response.json()
                # Check if any item has a URL containing this Confluence page ID
                for item in items:
                    raw_text = item.get('raw_text', '')
                    # Extract URL from raw_text (format: "URL: {url}\n\n{content}")
                    if raw_text.startswith('URL:'):
                        url_line = raw_text.split('\n')[0]
                        item_url = url_line.replace('URL:', '').strip()
                        # Check if the Confluence page ID is in the URL
                        if page_id in item_url or page_id in str(item.get('id', '')):
                            return item
        except Exception as e:
            logger.warning(f"Error checking for existing article: {e}")
        
        return None
    
    def _insert_article(self, article_data: Dict[str, Any]) -> bool:
        """Insert new article into Supabase."""
        # Generate AI summary if OpenAI is available
        summary_text = article_data.get('title', '')
        key_points = []
        decisions = []
        action_items = []
        
        if self.openai_api_key and article_data.get('text_content'):
            summary_data = self.summarize_article_with_openai(
                article_data.get('title', ''),
                article_data.get('text_content', '')
            )
            if summary_data:
                # Format summary for storage
                summary_text = self.format_ai_summary_for_storage(summary_data)
                key_points = summary_data.get('key_points', [])
                logger.info(f"Generated AI summary for article: {article_data.get('title', '')}")
            else:
                # Fallback to title if AI summary fails
                summary_text = article_data.get('title', '')
        else:
            # No AI, just use title
            summary_text = article_data.get('title', '')
        
        # For Confluence: store the AI-generated summary or title
        payload = {
            'summary': summary_text,
            'topics': [],  # Confluence articles don't have keyword-based topics
            'decisions': decisions,
            'key_points': key_points,
            'action_items': action_items,
            'faqs': [],
            'source': 'confluence',
            'date': article_data['date'],
            'project': self.space_key,  # Use space key as project
            'sender_name': article_data['author'],
            'raw_text': article_data.get('raw_text', ''),
        }
        
        # Add URL, title, and version info to raw_text header for duplicate detection
        url_line = f"URL: {article_data.get('url', '')}"
        title_line = f"CONFLUENCE_PAGE_TITLE: {article_data.get('title', '')}"
        version_line = f"CONFLUENCE_PAGE_ID: {article_data.get('id', '')}"
        version_num_line = f"CONFLUENCE_VERSION: {article_data.get('version', 1)}"
        version_date_line = f"CONFLUENCE_VERSION_DATE: {article_data.get('version_date', '')}"
        
        header = f"{url_line}\n{title_line}\n{version_line}\n{version_num_line}\n{version_date_line}\n\n"
        payload['raw_text'] = header + payload['raw_text']
        
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/knowledge_items",
                headers=self.supabase_headers,
                data=json.dumps(payload)
            )
            
            if response.status_code in (200, 201):
                logger.info(f"✅ Inserted article: {article_data['title']}")
                return True
            else:
                logger.error(f"Failed to insert article: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error inserting article: {e}")
            return False
    
    def _update_article(self, article_id: str, article_data: Dict[str, Any]) -> bool:
        """Update existing article in Supabase."""
        # Generate AI summary if OpenAI is available
        summary_text = article_data.get('title', '')
        key_points = []
        decisions = []
        action_items = []
        
        if self.openai_api_key and article_data.get('text_content'):
            summary_data = self.summarize_article_with_openai(
                article_data.get('title', ''),
                article_data.get('text_content', '')
            )
            if summary_data:
                # Format summary for storage
                summary_text = self.format_ai_summary_for_storage(summary_data)
                key_points = summary_data.get('key_points', [])
                logger.info(f"Generated AI summary for updated article: {article_data.get('title', '')}")
            else:
                # Fallback to title if AI summary fails
                summary_text = article_data.get('title', '')
        else:
            # No AI, just use title
            summary_text = article_data.get('title', '')
        
        payload = {
            'summary': summary_text,
            'date': article_data['date'],
            'sender_name': article_data['author'],
            'raw_text': article_data.get('raw_text', ''),
            'key_points': key_points,
            'decisions': decisions,
            'action_items': action_items,
        }
        
        # Add URL, title, and version info to raw_text header
        url_line = f"URL: {article_data.get('url', '')}"
        title_line = f"CONFLUENCE_PAGE_TITLE: {article_data.get('title', '')}"
        version_line = f"CONFLUENCE_PAGE_ID: {article_data.get('id', '')}"
        version_num_line = f"CONFLUENCE_VERSION: {article_data.get('version', 1)}"
        version_date_line = f"CONFLUENCE_VERSION_DATE: {article_data.get('version_date', '')}"
        
        header = f"{url_line}\n{title_line}\n{version_line}\n{version_num_line}\n{version_date_line}\n\n"
        payload['raw_text'] = header + payload['raw_text']
        
        try:
            response = requests.patch(
                f"{self.supabase_url}/rest/v1/knowledge_items?id=eq.{article_id}",
                headers={**self.supabase_headers, "Prefer": "return=representation"},
                data=json.dumps(payload)
            )
            
            if response.status_code in (200, 204):
                logger.info(f"🔄 Updated article: {article_data['title']}")
                return True
            else:
                logger.error(f"Failed to update article: {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error updating article: {e}")
            return False
    
    def _extract_version_from_raw_text(self, raw_text: str) -> tuple:
        """Extract Confluence page ID and version from raw_text header."""
        page_id = None
        version = None
        version_date = None
        
        if not raw_text:
            return (page_id, version, version_date)
        
        lines = raw_text.split('\n')
        for line in lines[:10]:  # Check first 10 lines for metadata
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
    
    def save_to_supabase(self, article_data: Dict[str, Any]) -> bool:
        """Insert or update article in Supabase only if version changed."""
        page_id = article_data.get('id')
        if not page_id:
            logger.error("Article data missing page ID")
            return False
        
        page_url = article_data.get('url', '')
        existing = self._find_existing_article(page_id, page_url)
        
        if existing:
            # Extract version info from existing article
            existing_raw_text = existing.get('raw_text', '')
            existing_page_id, existing_version, existing_version_date = self._extract_version_from_raw_text(existing_raw_text)
            
            # Get current version info
            current_version = article_data.get('version', 1)
            current_version_date = article_data.get('version_date', '')
            
            # Compare versions - only update if version number increased or version date is newer
            should_update = False
            
            if existing_version is not None and current_version is not None:
                if current_version > existing_version:
                    should_update = True
                    logger.info(f"Version changed: {existing_version} -> {current_version} for page {page_id}")
                elif current_version == existing_version and current_version_date != existing_version_date:
                    # Same version number but different date (shouldn't happen, but check anyway)
                    should_update = True
                    logger.info(f"Version date changed for page {page_id}")
            else:
                # If we can't determine version, compare dates
                existing_date = existing.get('date', '')
                current_date = article_data.get('date', '')
                if current_date > existing_date:
                    should_update = True
                    logger.info(f"Date changed: {existing_date} -> {current_date} for page {page_id}")
                elif current_date == existing_date:
                    # Same date, check if content might have changed by comparing updated_at
                    existing_updated = existing.get('updated_at', '')
                    if existing_updated:
                        try:
                            existing_updated_dt = datetime.fromisoformat(existing_updated.replace('Z', '+00:00'))
                            current_timestamp = article_data.get('version_timestamp', datetime.now().timestamp())
                            current_dt = datetime.fromtimestamp(current_timestamp)
                            if current_dt > existing_updated_dt:
                                should_update = True
                                logger.info(f"Content updated for page {page_id}")
                        except Exception:
                            # If date parsing fails, update to be safe
                            should_update = True
            
            if should_update:
                return self._update_article(existing['id'], article_data)
            else:
                logger.info(f"⏭️  Skipping page {page_id} ({article_data.get('title', 'Unknown')}) - no changes detected")
                return True  # Return True because it's not an error, just no update needed
        else:
            return self._insert_article(article_data)
    
    # ========================================================================
    # Main Workflow
    # ========================================================================
    
    def run_extraction_workflow(self) -> bool:
        """Execute the complete extraction workflow."""
        try:
            logger.info("=" * 60)
            logger.info("Starting Confluence Knowledge Extraction Workflow")
            logger.info("=" * 60)
            
            # Fetch pages from Confluence
            pages = self.fetch_confluence_pages()
            if not pages:
                logger.warning("No pages found in Confluence space")
                return True
            
            # Process each page
            stats = {'processed': 0, 'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
            
            for page in pages:
                stats['processed'] += 1
                
                article_data = self.extract_page_data(page)
                if not article_data:
                    stats['errors'] += 1
                    continue
                
                page_id = article_data.get('id', '')
                page_url = article_data.get('url', '')
                existing = self._find_existing_article(page_id, page_url)
                
                success = self.save_to_supabase(article_data)
                if success:
                    # Check if it was an insert, update, or skip
                    if not existing:
                        stats['inserted'] += 1
                    else:
                        # Check if it was actually updated or skipped
                        existing_raw_text = existing.get('raw_text', '')
                        existing_page_id, existing_version, existing_version_date = self._extract_version_from_raw_text(existing_raw_text)
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


# ============================================================================
# Entry Point
# ============================================================================

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

