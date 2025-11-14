#!/usr/bin/env python3
"""
Slack Keyword Dedup Extractor
- Loads keywords/key phrases from backend and frontend README files
- Fetches Slack messages from specified channel(s)
- Matches messages containing any keyword/phrase (no formatting)
- Deduplicates by Slack ts or content hash against Supabase
- Inserts only new messages into Supabase with details

Config via environment variables (.env):
- SLACK_BOT_TOKEN
- SUPABASE_URL
- SUPABASE_ANON_KEY
- INCLUDE_CHANNELS (comma-separated, e.g., all-knowledgehub,eng-updates) optional
- EXTRACTION_HOURS_BACK (default 24)
"""

import os
import sys
import re
import json
import hashlib
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta

import requests

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dataclasses
@dataclass
class SlackMsg:
    ts: str
    text: str
    user: str
    channel_id: str
    channel_name: str

# Helpers
def load_env_str(name: str, default: Optional[str] = None) -> str:
    val = os.getenv(name, default)
    if val is None:
        logger.error(f"Missing required env var: {name}")
        sys.exit(1)
    return val

def read_file_text(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Could not read {path}: {e}")
        return ""

def normalize_text_for_match(text: str) -> str:
    # Remove common formatting characters and normalize spaces
    text = text.replace('`', ' ').replace('*', ' ').replace('_', ' ').replace('~', ' ')
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

def extract_keywords_from_readmes(frontend_path: str, backend_path: str) -> List[str]:
    fe = read_file_text(frontend_path)
    be = read_file_text(backend_path)
    combined = f"{fe}\n{be}"

    # Look for explicit keyword sections/bullets first
    candidates: Set[str] = set()

    # Capture list items after headings that mention Keywords
    for m in re.finditer(r"(?im)^##\s*(?:🚩\s*)?Important\s+Keywords[\s\S]*?$", combined):
        pass  # placeholder; below general bullet parsing covers it

    # Collect bullet items and inline code tokens
    bullet_items = re.findall(r"(?m)^\s*[-*]\s+(.+)$", combined)
    code_items = re.findall(r"`([^`]+)`", combined)

    for item in bullet_items + code_items:
        cleaned = normalize_text_for_match(item)
        # Keep short phrases/words; strip trailing punctuation
        cleaned = re.sub(r"[\s,:;.!?]+$", "", cleaned)
        # Skip overly generic terms
        if not cleaned:
            continue
        if len(cleaned) < 2:
            continue
        # Limit phrase length to avoid entire sentences
        if len(cleaned.split()) <= 4:
            candidates.add(cleaned)

    # Additionally, seed with known terms often used in this repo
    seeded = [
        'ui issues', 'dashboard', 'mia chatbot', 'recommendations', 'order history',
        'pending approvals', 'catalog', 'cart', 'authentication', 'rest api',
        'dental city webhook', 'mia chat api'
    ]
    for s in seeded:
        candidates.add(normalize_text_for_match(s))

    # Remove duplicates and return
    keywords = sorted(candidates)
    logger.info(f"Loaded {len(keywords)} keywords/phrases from README files")
    return keywords

# Slack API
class SlackClient:
    def __init__(self, token: str):
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def list_channels(self) -> List[Dict]:
        url = "https://slack.com/api/conversations.list"
        resp = requests.get(url, headers=self.headers)
        data = resp.json()
        if not data.get('ok'):
            raise RuntimeError(f"Slack error conversations.list: {data.get('error')}")
        return data.get('channels', [])

    def fetch_history(self, channel_id: str, oldest_ts: str, limit: int = 200) -> List[Dict]:
        url = "https://slack.com/api/conversations.history"
        params = { 'channel': channel_id, 'oldest': oldest_ts, 'limit': limit }
        resp = requests.get(url, headers=self.headers, params=params)
        data = resp.json()
        if not data.get('ok'):
            raise RuntimeError(f"Slack error conversations.history: {data.get('error')}")
        return data.get('messages', [])

# Supabase REST
class SupabaseClient:
    def __init__(self, url: str, anon_key: str):
        self.url = url.rstrip('/')
        self.headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Content-Type': 'application/json'
        }

    def exists_message(self, ts: str, content_hash: str) -> bool:
        # Check by ts in date OR hash stored in raw_text
        # First by date==ts and source==Slack Message
        params = {
            'select': 'id',
            'date': f'eq.{ts}',
            'source': 'eq.Slack Message'
        }
        resp = requests.get(f"{self.url}/rest/v1/knowledge_items", headers=self.headers, params=params)
        if resp.status_code == 200 and resp.json():
            return True
        # Fallback: search by hash contained (simple contains filter not supported; fetch few latest and scan)
        params2 = { 'select': 'id,raw_text', 'order': 'created_at.desc', 'limit': 100 }
        resp2 = requests.get(f"{self.url}/rest/v1/knowledge_items", headers=self.headers, params=params2)
        if resp2.status_code == 200:
            for row in resp2.json():
                if row.get('raw_text') and content_hash in row['raw_text']:
                    return True
        return False

    def insert_message(self, summary: str, matched_keyword: str, msg: SlackMsg, content_hash: str) -> bool:
        payload = {
            'summary': summary,
            'topics': [matched_keyword],
            'decisions': [],
            'faqs': [],
            'source': 'Slack Message',
            'date': msg.ts,  # store ts for dedup
            'project': 'Slack',
            'raw_text': (
                f"message_id: {msg.ts}\n"
                f"hash: {content_hash}\n"
                f"channel: #{msg.channel_name} ({msg.channel_id})\n"
                f"user: {msg.user}\n"
                f"message: {msg.text}"
            )
        }
        resp = requests.post(f"{self.url}/rest/v1/knowledge_items", headers=self.headers, data=json.dumps(payload))
        if resp.status_code in (200, 201):
            return True
        logger.error(f"Supabase insert failed: {resp.status_code} {resp.text}")
        return False

# Matching
def message_matches_keywords(text: str, keywords: List[str]) -> Optional[str]:
    norm = normalize_text_for_match(text)
    for kw in keywords:
        # Exact phrase search on normalized content
        kw_norm = normalize_text_for_match(kw)
        if not kw_norm:
            continue
        # For single words, enforce word boundary; for phrases, substring
        if ' ' in kw_norm:
            if kw_norm in norm:
                return kw
        else:
            if re.search(rf"\b{re.escape(kw_norm)}\b", norm):
                return kw
    return None

# Main workflow
def main():
    slack_token = load_env_str('SLACK_BOT_TOKEN')
    supabase_url = load_env_str('SUPABASE_URL')
    supabase_key = load_env_str('SUPABASE_ANON_KEY')

    # Channels to include
    include_channels_raw = os.getenv('INCLUDE_CHANNELS', '')
    include_channels = [c.strip().lower() for c in include_channels_raw.split(',') if c.strip()]

    hours_back = int(os.getenv('EXTRACTION_HOURS_BACK', '24'))
    oldest_ts = str(int((datetime.now() - timedelta(hours=hours_back)).timestamp()))

    # Read keywords
    repo_root = os.getcwd()
    fe_readme = os.path.join(repo_root, 'frontend', 'README.md')
    be_readme = os.path.join(repo_root, 'backend', 'README.md')
    keywords = extract_keywords_from_readmes(fe_readme, be_readme)
    if not keywords:
        logger.warning('No keywords found; exiting')
        return 0

    slack = SlackClient(slack_token)
    supa = SupabaseClient(supabase_url, supabase_key)

    # Channels
    channels = slack.list_channels()
    selected: List[Tuple[str, str]] = []  # (id, name)
    for ch in channels:
        name = ch.get('name', '').lower()
        if ch.get('is_archived'):
            continue
        if include_channels and name not in include_channels:
            continue
        selected.append((ch['id'], ch['name']))

    if not selected:
        logger.warning('No channels selected (check INCLUDE_CHANNELS)')
        return 0

    inserted = 0
    scanned = 0

    for ch_id, ch_name in selected:
        try:
            messages = slack.fetch_history(ch_id, oldest_ts, limit=200)
        except Exception as e:
            logger.error(f"Failed fetching history for #{ch_name}: {e}")
            continue

        for m in messages:
            # Skip bot/system
            if m.get('bot_id') or m.get('subtype'):
                continue
            text = m.get('text') or ''
            if not text.strip():
                continue

            scanned += 1
            match = message_matches_keywords(text, keywords)
            if not match:
                continue

            ts = m.get('ts', '')
            user = m.get('user', 'unknown')
            msg = SlackMsg(ts=ts, text=text, user=user, channel_id=ch_id, channel_name=ch_name)
            content_hash = hashlib.sha256(normalize_text_for_match(text).encode('utf-8')).hexdigest()

            # Dedup check
            if supa.exists_message(ts, content_hash):
                continue

            summary = f"Slack #{ch_name} | user:{user} | ts:{ts} | kw:{match}"
            if supa.insert_message(summary, match, msg, content_hash):
                inserted += 1

    logger.info(f"Scanned messages: {scanned} | Inserted new: {inserted}")
    return 0

if __name__ == '__main__':
    sys.exit(main())


