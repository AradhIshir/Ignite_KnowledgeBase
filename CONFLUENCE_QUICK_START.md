# Confluence Extractor - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Get Confluence API Token
- Visit: https://id.atlassian.com/manage-profile/security/api-tokens
- Click "Create API token"
- Copy the token

### 2. Find Your Space Key
- Go to your Confluence space
- Look at the URL: `.../spaces/SPACEKEY/...`
- Copy the SPACEKEY (e.g., "PROJ", "ENG")

### 3. Add to .env File
Add these lines to your `.env` file:

```bash
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=paste-your-token-here
CONFLUENCE_SPACE_KEY=SPACEKEY
```

### 4. Run It!

**Option A - Simple command:**
```bash
export $(cat .env | grep -v '^#' | xargs) && python3 confluence_knowledge_extractor.py
```

**Option B - Using script:**
```bash
./run_confluence_extractor.sh
```

## ✅ That's It!

The script will:
- ✅ Connect to Confluence
- ✅ Fetch pages from your space
- ✅ Save them to Supabase
- ✅ Show you what was done

## 📊 What You'll See

```
🚀 Starting Confluence Knowledge Extractor...
✅ Environment variables loaded
📥 Fetching articles from Confluence...

Fetching pages from Confluence space: PROJ
Fetched 25 pages (total: 25)
✅ Inserted article: Getting Started Guide
✅ Inserted article: API Documentation
🔄 Updated article: User Manual
...
✅ Extraction completed:
   Processed: 25 pages
   Inserted: 20 new articles
   Updated: 5 existing articles
   Errors: 0
```

## ❓ Common Issues

**"Missing required environment variables"**
→ Check your `.env` file has all the Confluence variables

**"401 Unauthorized"**
→ Check your email and API token are correct

**"404 Not Found"**
→ Check your Confluence URL and space key

## 📖 Full Documentation

See `CONFLUENCE_EXTRACTOR_SETUP.md` for detailed instructions.

