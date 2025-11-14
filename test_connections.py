#!/usr/bin/env python3
"""
Test script to verify Slack and Supabase connections
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

print("🔍 Testing Slack Connection...")
print(f"Slack Token: {env['SLACK_BOT_TOKEN'][:20]}...")

# Test Slack API
slack_url = "https://slack.com/api/auth.test"
slack_headers = {
    'Authorization': f"Bearer {env['SLACK_BOT_TOKEN']}",
    'Content-Type': 'application/json'
}

try:
    response = requests.get(slack_url, headers=slack_headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            print("✅ Slack connection successful!")
            print(f"   Bot: {data.get('user')}")
            print(f"   Team: {data.get('team')}")
        else:
            print(f"❌ Slack API error: {data.get('error')}")
    else:
        print(f"❌ Slack HTTP error: {response.status_code}")
except Exception as e:
    print(f"❌ Slack connection failed: {str(e)}")

print("\n🔍 Testing Supabase Connection...")
print(f"Supabase URL: {env['SUPABASE_URL']}")
print(f"Supabase Email: {env['SUPABASE_EMAIL']}")

# Test Supabase authentication
supabase_url = f"{env['SUPABASE_URL']}/auth/v1/token?grant_type=password"
supabase_headers = {
    'apikey': env['SUPABASE_ANON_KEY'],
    'Content-Type': 'application/json'
}
supabase_data = {
    'email': env['SUPABASE_EMAIL'],
    'password': env['SUPABASE_PASSWORD']
}

try:
    response = requests.post(supabase_url, headers=supabase_headers, json=supabase_data)
    if response.status_code == 200:
        data = response.json()
        if 'access_token' in data:
            print("✅ Supabase authentication successful!")
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
        else:
            print(f"❌ Supabase auth error: {data}")
    else:
        print(f"❌ Supabase HTTP error: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Supabase connection failed: {str(e)}")

print("\n🔍 Testing Supabase Database Access...")
# Test database access
db_url = f"{env['SUPABASE_URL']}/rest/v1/knowledge_items?select=count"
db_headers = {
    'apikey': env['SUPABASE_ANON_KEY'],
    'Authorization': f"Bearer {env['SUPABASE_ANON_KEY']}"
}

try:
    response = requests.get(db_url, headers=db_headers)
    if response.status_code == 200:
        print("✅ Supabase database access successful!")
        print(f"   Response: {response.text}")
    else:
        print(f"❌ Supabase database error: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Supabase database connection failed: {str(e)}")




