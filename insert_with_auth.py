#!/usr/bin/env python3
"""
Script to insert knowledge item into Supabase database with authentication.
"""
import requests
import json
import sys

# Supabase configuration
SUPABASE_URL = "https://wwmqodqqqrffxdvgisrd.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3bXFvZHFxcXJmZnhkdmdpc3JkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNzkwODIsImV4cCI6MjA3Njg1NTA4Mn0.Af0VXHqBc-rEHy8jbcXcCakpPFfyE_B_koOAiAS_ZcI"

# Test user credentials
TEST_EMAIL = "admin@igniteknowledge.com"
TEST_PASSWORD = "AragoIshir@123"

# Knowledge item data
knowledge_item = {
    "summary": "Project Keywords and Technical Stack Documentation - Extracted main keywords from Ignite Knowledge project covering full-stack architecture, technologies, features, and development workflow",
    "topics": [
        "Next.js", "TypeScript", "React", "Styled Components", "FastAPI", 
        "Python", "Poetry", "Supabase", "PostgreSQL", "Authentication", 
        "Knowledge Management", "Full-Stack Development", "RESTful API", 
        "Row-Level Security", "Real-time Subscriptions", "CSV Export", 
        "PDF Export", "Search & Filtering", "Dashboard", "Responsive Design"
    ],
    "decisions": [
        "Use Next.js 14.2.5 for frontend framework",
        "Implement FastAPI for backend services",
        "Choose Supabase for database and authentication",
        "Use Styled Components for styling solution",
        "Implement Poetry for Python dependency management",
        "Enable CORS for cross-origin requests",
        "Use Row-Level Security policies for data protection",
        "Implement real-time subscriptions for live updates",
        "Create modular component-based architecture",
        "Support CSV and PDF export formats"
    ],
    "faqs": [
        "Q: What technologies are used? A: Next.js, FastAPI, Supabase, TypeScript, React, Styled Components",
        "Q: What ports does the application use? A: Frontend runs on port 3000, Backend on port 8080",
        "Q: How to setup the project? A: Install Node.js 18+, Python 3.10+, run npm install in frontend, poetry install in backend",
        "Q: What is the database schema? A: Main tables are knowledge_items, user_favorites, and activity_log",
        "Q: What features are available? A: Knowledge management, search & filtering, export, authentication, dashboard",
        "Q: Is the project production ready? A: Yes, version 1.0.0 is fully functional and production ready",
        "Q: What export formats are supported? A: CSV and PDF export via backend API",
        "Q: How is authentication handled? A: Supabase Auth with signup/signin and session management"
    ],
    "source": "Agent Thread - Knowledge Base Extraction Task",
    "date": "2025-10-27",
    "project": "Ignite Knowledge",
    "raw_text": """Full-Stack Knowledge Management Application

FRONTEND STACK:
- Next.js 14.2.5 with TypeScript
- React with hooks (useState, useEffect)
- Styled Components for CSS-in-JS
- Supabase Client for data access
- Responsive design across all devices

BACKEND STACK:
- FastAPI with Python 3.10+
- Poetry for dependency management
- Uvicorn ASGI server
- WeasyPrint for PDF generation
- CORS middleware enabled

DATABASE:
- Supabase PostgreSQL database
- Tables: knowledge_items, user_favorites, activity_log
- UUID primary keys
- Row-Level Security policies
- Real-time subscriptions

KEY FEATURES:
- Knowledge article creation and management
- Full-text search and filtering
- Multi-select project and topic filters
- CSV/PDF export functionality
- User authentication and authorization
- Real-time statistics dashboard
- Summary cards with article, project, and topic counts
- Responsive card-based layout
- User profile management

ARCHITECTURE:
- Frontend (Port 3000): Next.js App Router
- Backend (Port 8080): FastAPI REST API
- Database: Supabase cloud PostgreSQL
- Authentication: Supabase Auth with RLS

DEVELOPMENT:
- Frontend: npm install && npm run dev
- Backend: poetry install && poetry run python app/main.py
- Environment variables configured in .env.local

STATUS: Production Ready (v1.0.0)
Last Updated: October 27, 2025"""
}

def signup_user():
    """Sign up a new user."""
    print("Step 1: Attempting to sign up user...")
    
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Signup response status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ User signed up successfully!")
        result = response.json()
        if 'access_token' in result:
            print(f"Access token received during signup!")
            return result['access_token']
        return result
    else:
        print(f"Signup response: {response.text}")
        return None

def signin_user():
    """Sign in and get access token."""
    print("\nStep 2: Signing in to get access token...")
    
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        if access_token:
            print("✅ Successfully authenticated!")
            return access_token
        else:
            print("❌ No access token in response")
            return None
    else:
        print(f"❌ Sign in failed: {response.text}")
        return None

def insert_knowledge_item(access_token):
    """Insert knowledge item into Supabase."""
    print("\nStep 3: Inserting knowledge item into Supabase...")
    
    url = f"{SUPABASE_URL}/rest/v1/knowledge_items"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.post(url, headers=headers, json=knowledge_item)
    
    if response.status_code in [200, 201]:
        print("✅ Successfully inserted knowledge item!")
        print("\nResponse:")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"❌ Error inserting knowledge item:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    """Main execution function."""
    print("=" * 60)
    print("Knowledge Base Insertion Script")
    print("=" * 60)
    
    # Try to sign up first
    access_token = signup_user()
    
    # If no token from signup, try to sign in
    if not access_token:
        access_token = signin_user()
    
    if not access_token:
        print("\n❌ Could not authenticate. Please check your credentials.")
        return 1
    
    # Try to insert knowledge item
    success = insert_knowledge_item(access_token)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Knowledge item successfully added to Supabase!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Failed to insert knowledge item")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(main())
