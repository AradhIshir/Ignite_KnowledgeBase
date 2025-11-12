#!/bin/bash
# Confluence Knowledge Extractor - Wrapper Script
# This script loads environment variables and runs the Confluence extractor

echo "🚀 Starting Confluence Knowledge Extractor..."
echo ""

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env file"
else
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your Confluence and Supabase credentials."
    exit 1
fi

# Check if required variables are set
if [ -z "$CONFLUENCE_URL" ] || [ -z "$CONFLUENCE_EMAIL" ] || [ -z "$CONFLUENCE_API_TOKEN" ]; then
    echo "❌ Error: Missing Confluence credentials in .env file"
    echo "Required: CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN"
    exit 1
fi

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "❌ Error: Missing Supabase credentials in .env file"
    echo "Required: SUPABASE_URL, SUPABASE_ANON_KEY"
    exit 1
fi

# Run the extractor
echo "📥 Fetching articles from Confluence..."
echo ""
python3 confluence_knowledge_extractor.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ Confluence extraction completed successfully!"
else
    echo ""
    echo "❌ Confluence extraction failed. Check the logs for details."
fi

exit $exit_code

