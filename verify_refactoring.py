#!/usr/bin/env python3
"""Quick verification script to ensure refactored code imports correctly."""
import sys
import os

def verify_imports():
    """Verify that all refactored modules can be imported."""
    errors = []
    
    # Add backend to path
    backend_path = os.path.join(os.path.dirname(__file__), 'backend')
    if os.path.exists(backend_path):
        sys.path.insert(0, backend_path)
    
    # Test backend imports
    try:
        from app.utils.text_processing import normalize_text, clean_slack_message
        from app.utils.date_utils import format_date_readable
        from app.utils.ai_summarization import call_openai_api
        from app.utils.api_clients import ConfluenceAPIClient, SlackAPIClient, SupabaseAPIClient
        from app.models import ExportRequest, CreateUserRequest
        from app.services.export_service import to_csv, to_pdf
        from app.services.user_service import UserService
        from app.auth import verify_admin
        print("✅ Backend utilities import successfully")
    except ImportError as e:
        errors.append(f"Backend import error: {e}")
        print(f"❌ Backend import failed: {e}")
    
    # Test extractor syntax
    try:
        with open('confluence_knowledge_extractor.py', 'r') as f:
            compile(f.read(), 'confluence_knowledge_extractor.py', 'exec')
        print("✅ Confluence extractor syntax valid")
    except SyntaxError as e:
        errors.append(f"Confluence extractor syntax error: {e}")
        print(f"❌ Confluence extractor syntax error: {e}")
    
    try:
        with open('slack_knowledge_extractor_simple.py', 'r') as f:
            compile(f.read(), 'slack_knowledge_extractor_simple.py', 'exec')
        print("✅ Slack extractor syntax valid")
    except SyntaxError as e:
        errors.append(f"Slack extractor syntax error: {e}")
        print(f"❌ Slack extractor syntax error: {e}")
    
    try:
        with open('backend/app/main.py', 'r') as f:
            compile(f.read(), 'backend/app/main.py', 'exec')
        print("✅ Backend main.py syntax valid")
    except SyntaxError as e:
        errors.append(f"Backend main.py syntax error: {e}")
        print(f"❌ Backend main.py syntax error: {e}")
    
    if errors:
        print(f"\n❌ Found {len(errors)} error(s)")
        return False
    else:
        print("\n✅ All refactored code verified successfully!")
        return True

if __name__ == '__main__':
    success = verify_imports()
    sys.exit(0 if success else 1)

