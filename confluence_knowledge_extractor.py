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
- CONFLUENCE_LIMIT (optional): Maximum number of pages to fetch (default: 50)
"""
import os
import sys
import json
import logging
import requests
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
        
        self._validate_environment()
        self._setup_api_headers()
        logger.info("ConfluenceKnowledgeExtractor initialized successfully")
    
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
            
            # Extract summary (first 200 characters of content, stripped of HTML and decoded)
            import re
            import html
            # Remove HTML tags for summary
            text_content = re.sub(r'<[^>]+>', '', body_storage)
            # Decode HTML entities
            text_content = html.unescape(text_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
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
            
            # Get date
            version_date = page.get('version', {}).get('when', '')
            if version_date:
                try:
                    # Parse ISO format date
                    date_obj = datetime.fromisoformat(version_date.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d')
                except Exception:
                    date_str = datetime.now().strftime('%Y-%m-%d')
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            return {
                'id': page_id,
                'title': title,
                'summary': summary,
                'url': page_url,
                'author': author,
                'date': date_str,
                'source': 'confluence',
                'raw_text': body_storage  # Store full HTML content
            }
        except Exception as e:
            logger.error(f"Error extracting data from page {page.get('id', 'unknown')}: {e}")
            return None
    
    # ========================================================================
    # Supabase Methods
    # ========================================================================
    
    def _find_existing_article(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Find existing article in Supabase by checking URL or title."""
        # Try to find by URL first (most reliable)
        params = {
            'select': 'id,url,title',
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
                # Check if any item has a URL containing this page ID
                for item in items:
                    item_url = item.get('url', '')
                    if page_id in item_url or page_id in str(item.get('id', '')):
                        return item
        except Exception as e:
            logger.warning(f"Error checking for existing article: {e}")
        
        return None
    
    def _insert_article(self, article_data: Dict[str, Any]) -> bool:
        """Insert new article into Supabase."""
        # For Confluence: store the actual page title in summary field
        # The content preview will be extracted from raw_text in the frontend
        payload = {
            'summary': article_data['title'],  # Store actual Confluence page title
            'topics': [],  # Confluence articles don't have keyword-based topics
            'decisions': [],
            'faqs': [],
            'source': 'confluence',
            'date': article_data['date'],
            'project': self.space_key,  # Use space key as project
            'sender_name': article_data['author'],
            'raw_text': article_data.get('raw_text', ''),
            # Store additional metadata in raw_text or use custom fields if available
        }
        
        # Add URL if your schema supports it (you may need to add a url column)
        # For now, we'll store it in raw_text header
        if article_data.get('url'):
            payload['raw_text'] = f"URL: {article_data['url']}\n\n{payload['raw_text']}"
        
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
        payload = {
            'summary': article_data['title'],  # Store actual Confluence page title
            'date': article_data['date'],
            'sender_name': article_data['author'],
            'raw_text': article_data.get('raw_text', ''),
        }
        
        if article_data.get('url'):
            payload['raw_text'] = f"URL: {article_data['url']}\n\n{payload['raw_text']}"
        
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
    
    def save_to_supabase(self, article_data: Dict[str, Any]) -> bool:
        """Insert or update article in Supabase."""
        page_id = article_data.get('id')
        if not page_id:
            logger.error("Article data missing page ID")
            return False
        
        existing = self._find_existing_article(page_id)
        
        if existing:
            return self._update_article(existing['id'], article_data)
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
            stats = {'processed': 0, 'inserted': 0, 'updated': 0, 'errors': 0}
            
            for page in pages:
                stats['processed'] += 1
                
                article_data = self.extract_page_data(page)
                if not article_data:
                    stats['errors'] += 1
                    continue
                
                success = self.save_to_supabase(article_data)
                if success:
                    # Check if it was an insert or update by checking if we found existing
                    existing = self._find_existing_article(article_data['id'])
                    if existing and existing.get('id'):
                        stats['updated'] += 1
                    else:
                        stats['inserted'] += 1
                else:
                    stats['errors'] += 1
            
            logger.info("=" * 60)
            logger.info(f"✅ Extraction completed:")
            logger.info(f"   Processed: {stats['processed']} pages")
            logger.info(f"   Inserted: {stats['inserted']} new articles")
            logger.info(f"   Updated: {stats['updated']} existing articles")
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

