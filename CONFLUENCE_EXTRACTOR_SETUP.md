# Confluence Knowledge Extractor - Setup Guide

This guide will help you set up and run the Confluence extractor to fetch articles from Confluence and save them to Supabase.

## 📋 Prerequisites

1. **Confluence Cloud Account** with access to the space you want to extract
2. **Confluence API Token** (see instructions below)
3. **Supabase Account** with your project URL and API key
4. **Python 3.7+** installed on your system

## 🔑 Step 1: Get Your Confluence API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Give it a label (e.g., "Knowledge Extractor")
4. Click **"Create"**
5. **Copy the token immediately** - you won't be able to see it again!

## 📝 Step 2: Find Your Confluence Space Key

1. Go to your Confluence space
2. Look at the URL - it will be something like:
   - `https://your-domain.atlassian.net/wiki/spaces/SPACEKEY/...`
   - The `SPACEKEY` is what you need (e.g., "PROJ", "ENG", "~username")

## ⚙️ Step 3: Configure Environment Variables

Add these variables to your `.env` file in the project root:

```bash
# Confluence Configuration
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token-here
CONFLUENCE_SPACE_KEY=SPACEKEY
CONFLUENCE_LIMIT=50

# Supabase Configuration (you may already have these)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

### Example `.env` file:

```bash
# Confluence
CONFLUENCE_URL=https://mycompany.atlassian.net
CONFLUENCE_EMAIL=john.doe@mycompany.com
CONFLUENCE_API_TOKEN=ATATT3xFfGF0...
CONFLUENCE_SPACE_KEY=PROJ
CONFLUENCE_LIMIT=50

# Supabase
SUPABASE_URL=https://wwmqodqqqrffxdvgisrd.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🚀 Step 4: Run the Extractor

### Option 1: Direct Python Command

```bash
export $(cat .env | grep -v '^#' | xargs) && python3 confluence_knowledge_extractor.py
```

### Option 2: Using the Wrapper Script

```bash
chmod +x run_confluence_extractor.sh
./run_confluence_extractor.sh
```

## 📊 What Gets Extracted

For each Confluence page, the script extracts:

- **Title**: Page title
- **Summary**: First 200 characters of content (HTML stripped)
- **URL**: Direct link to the page
- **Author**: Page author/creator
- **Date**: Last modified date
- **Source**: Set to "confluence"
- **Content**: Full page content (stored in raw_text)

## 🔍 How It Works

1. **Connects** to Confluence Cloud REST API using your credentials
2. **Fetches** pages from the specified space (up to the limit you set)
3. **Extracts** title, summary, URL, author, and date from each page
4. **Checks** if the article already exists in Supabase (by URL/page ID)
5. **Inserts** new articles or **updates** existing ones
6. **Logs** all actions and results

## 📝 Logs

The script creates a log file: `confluence-extractor.log`

You can also see output in your terminal.

## ⚠️ Troubleshooting

### Error: "Missing required environment variables"
- Make sure all variables are set in your `.env` file
- Check that there are no typos in variable names
- Ensure no extra spaces around the `=` sign

### Error: "Confluence API error: 401 Unauthorized"
- Check your email address is correct
- Verify your API token is correct (generate a new one if needed)
- Make sure you have access to the space

### Error: "Confluence API error: 404 Not Found"
- Verify your Confluence URL is correct (should end with `.atlassian.net`)
- Check that the space key is correct
- Ensure you have access to the space

### Error: "Failed to insert article"
- Check your Supabase URL and API key
- Verify your Supabase table has the required columns
- Check Supabase logs for more details

## 🔒 Security Notes

- **Never commit** your `.env` file to version control
- **Keep your API tokens secure** - treat them like passwords
- **Rotate tokens** periodically for security
- The `.env` file is already in `.gitignore` to prevent accidental commits

## 📚 Additional Options

### Limit Number of Pages

Set `CONFLUENCE_LIMIT` to control how many pages to fetch:
- `CONFLUENCE_LIMIT=10` - Fetch only 10 pages
- `CONFLUENCE_LIMIT=100` - Fetch up to 100 pages
- Default is 50 if not specified

### Fetch Specific Pages

To fetch pages from multiple spaces, run the script multiple times with different `CONFLUENCE_SPACE_KEY` values.

## ✅ Success Indicators

When the script runs successfully, you'll see:

```
✅ Inserted article: Page Title 1
✅ Inserted article: Page Title 2
🔄 Updated article: Page Title 3
...
============================================================
✅ Extraction completed:
   Processed: 25 pages
   Inserted: 20 new articles
   Updated: 5 existing articles
   Errors: 0
============================================================
```

## 🆘 Need Help?

If you encounter issues:

1. Check the log file: `confluence-extractor.log`
2. Verify all environment variables are set correctly
3. Test your Confluence API access manually
4. Check Supabase table structure matches expected format

