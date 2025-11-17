#!/usr/bin/env python3
"""
Debug script to inspect Confluence HTML structure
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def get_confluence_article():
    """Fetch a Confluence article from Supabase to inspect its HTML structure."""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get Confluence articles - find "Discussions about Mia-latest"
    params = {
        'select': 'id,summary,raw_text,source',
        'source': 'eq.confluence',
        'limit': 10
    }
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/knowledge_items",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        items = response.json()
        if items:
            # Find the "Discussions about Mia-latest" article
            target_item = None
            for item in items:
                raw_text = item.get('raw_text', '')
                if 'Mia' in raw_text or 'Discussions' in raw_text:
                    target_item = item
                    break
            
            if not target_item:
                target_item = items[0]
            
            item = target_item
            print(f"Summary: {item.get('summary', 'N/A')[:100]}")
            print(f"\n{'='*80}")
            print("RAW HTML CONTENT (first 2000 chars):")
            print(f"{'='*80}\n")
            raw_text = item.get('raw_text', '')
            print(raw_text[:2000])
            print(f"\n{'='*80}")
            print("HTML CONTENT AFTER METADATA REMOVAL:")
            print(f"{'='*80}\n")
            
            # Simulate what extractConfluenceData does
            lines = raw_text.split('\n')
            contentStartIndex = 0
            
            for i in range(min(len(lines), 15)):
                line = lines[i].strip()
                if line.startswith('URL:') or line.startswith('CONFLUENCE_PAGE_TITLE:') or \
                   line.startswith('CONFLUENCE_PAGE_ID:') or line.startswith('CONFLUENCE_VERSION:') or \
                   line.startswith('CONFLUENCE_VERSION_DATE:'):
                    contentStartIndex = max(contentStartIndex, i + 1)
                elif line == '' and contentStartIndex <= i:
                    contentStartIndex = i + 1
                elif line and not any(line.startswith(prefix) for prefix in ['URL:', 'CONFLUENCE_PAGE_TITLE:', 'CONFLUENCE_PAGE_ID:', 'CONFLUENCE_VERSION:', 'CONFLUENCE_VERSION_DATE:']):
                    break
            
            html_content = '\n'.join(lines[contentStartIndex:]).strip()
            print(html_content[:2000])
            
            # Look for UUID patterns
            import re
            uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
            matches = re.findall(uuid_pattern, html_content[:2000], re.IGNORECASE)
            if matches:
                print(f"\n{'='*80}")
                print(f"Found {len(matches)} UUID patterns in first 2000 chars:")
                print(f"{'='*80}\n")
                for match in matches[:10]:  # Show first 10
                    print(f"  - {match}")
        else:
            print("No Confluence articles found")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == '__main__':
    get_confluence_article()

