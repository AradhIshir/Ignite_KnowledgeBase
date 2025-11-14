#!/usr/bin/env python3
"""
Test Supabase insertion with sample data
"""
import os
import requests
import json

# Load environment variables
def load_env():
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    return env_vars

env = load_env()

print("🧪 Testing Supabase Insertion with Sample Data...")

# Sample knowledge item
sample_data = {
    "summary": "Test Knowledge Extraction - Manual insertion to verify Supabase connectivity",
    "topics": ["Slack", "Integration", "Knowledge", "Management", "Testing"],
    "decisions": ["Test the Supabase insertion functionality", "Verify data structure compatibility"],
    "faqs": ["Q: Does Supabase insertion work? A: Testing now", "Q: Are the data types correct? A: Verifying"],
    "source": "Manual Test - Slack Knowledge Extractor",
    "date": "2025-10-28",
    "project": "Ignite Knowledge",
    "raw_text": "This is a test insertion to verify that the Supabase knowledge_items table can accept data from our Slack knowledge extractor system."
}

# Supabase configuration
supabase_url = f"{env['SUPABASE_URL']}/rest/v1/knowledge_items"
supabase_headers = {
    'apikey': env['SUPABASE_ANON_KEY'],
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {env['SUPABASE_ANON_KEY']}",
    'Prefer': 'return=representation'
}

try:
    print("📤 Sending data to Supabase...")
    response = requests.post(supabase_url, headers=supabase_headers, json=sample_data)
    
    if response.status_code in [200, 201]:
        print("✅ Successfully inserted test data into Supabase!")
        result = response.json()
        print(f"📊 Inserted record ID: {result[0].get('id')}")
        print(f"📝 Summary: {result[0].get('summary')}")
        print(f"🏷️  Topics: {result[0].get('topics')}")
        print(f"📅 Date: {result[0].get('date')}")
        print(f"📁 Project: {result[0].get('project')}")
    else:
        print(f"❌ Failed to insert into Supabase:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error inserting into Supabase: {str(e)}")

print("\n🔍 Checking current knowledge items count...")
try:
    count_url = f"{env['SUPABASE_URL']}/rest/v1/knowledge_items?select=count"
    count_response = requests.get(count_url, headers=supabase_headers)
    
    if count_response.status_code == 200:
        count_data = count_response.json()
        print(f"📊 Total knowledge items in database: {count_data[0]['count']}")
    else:
        print(f"❌ Failed to get count: {count_response.text}")
        
except Exception as e:
    print(f"❌ Error getting count: {str(e)}")




