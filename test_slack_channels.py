#!/usr/bin/env python3
"""
Test Slack channels and bot access
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

print("🔍 Testing Slack Channels and Bot Access...")

# Slack API configuration
slack_headers = {
    'Authorization': f"Bearer {env['SLACK_BOT_TOKEN']}",
    'Content-Type': 'application/json'
}

# Test 1: Get all channels
print("\n📋 Available Channels:")
try:
    channels_url = "https://slack.com/api/conversations.list"
    response = requests.get(channels_url, headers=slack_headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            channels = data.get('channels', [])
            print(f"Total channels: {len(channels)}")
            
            for channel in channels:
                channel_name = channel['name']
                channel_id = channel['id']
                is_member = channel.get('is_member', False)
                is_private = channel.get('is_private', False)
                is_archived = channel.get('is_archived', False)
                
                status = "✅ Member" if is_member else "❌ Not Member"
                private = "🔒 Private" if is_private else "🌐 Public"
                archived = "📦 Archived" if is_archived else "🟢 Active"
                
                print(f"  #{channel_name} ({channel_id}) - {status} {private} {archived}")
        else:
            print(f"❌ Slack API error: {data.get('error')}")
    else:
        print(f"❌ HTTP error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 2: Try to get messages from a specific channel
print("\n📨 Testing Message Access:")
try:
    # Try to get messages from general channel (if it exists)
    history_url = "https://slack.com/api/conversations.history"
    history_params = {
        'channel': 'C1234567890',  # This will fail, but let's see the error
        'limit': 5
    }
    
    response = requests.get(history_url, headers=slack_headers, params=history_params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            messages = data.get('messages', [])
            print(f"✅ Successfully fetched {len(messages)} messages")
        else:
            print(f"❌ API Error: {data.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n💡 Next Steps:")
print("1. Add the bot to channels where you want to extract knowledge")
print("2. Or use channels where the bot is already a member")
print("3. Test with a channel the bot can access")




