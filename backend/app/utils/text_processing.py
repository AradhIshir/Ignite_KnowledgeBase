"""Text processing utilities."""
import re
import hashlib
from typing import List


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


def hash_content(text: str) -> str:
    """Generate SHA256 hash of normalized text for deduplication."""
    return hashlib.sha256(normalize_text(text).encode('utf-8')).hexdigest()


def extract_text_from_html(html_content: str) -> str:
    """Extract plain text from HTML content."""
    import html as html_module
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    # Decode HTML entities
    text = html_module.unescape(text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_preview_text(text: str, max_words: int = 3) -> str:
    """Extract first N words for preview/description."""
    if not text:
        return ""
    words = text.strip().split()
    if len(words) >= max_words:
        return " ".join(words[:max_words]) + "..."
    elif words:
        return " ".join(words) + "..."
    return ""

