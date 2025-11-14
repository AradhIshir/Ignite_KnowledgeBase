#!/bin/bash
# Setup Cron Job for Slack Knowledge Extractor
# This script sets up the cron job to run every 10 minutes

echo "🚀 Setting up Slack Knowledge Extractor Cron Job..."

# Get current directory
CURRENT_DIR=$(pwd)
echo "📁 Working directory: $CURRENT_DIR"

# Create cron entry
CRON_ENTRY="*/10 * * * * cd $CURRENT_DIR && export \$(cat .env | grep -v '^#' | xargs) && python3 slack_knowledge_extractor_simple.py >> slack-extractor.log 2>&1"

echo "📅 Cron schedule: Every 10 minutes"
echo "📝 Log file: slack-extractor.log"

# Add to crontab
echo "Adding cron job..."
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job installed successfully!"
    echo ""
    echo "📋 Current cron jobs:"
    crontab -l
    echo ""
    echo "🔍 To monitor the system:"
    echo "  tail -f slack-extractor.log"
    echo ""
    echo "🗑️  To remove the cron job:"
    echo "  crontab -e  # then delete the line"
    echo ""
    echo "🧪 To test manually:"
    echo "  export \$(cat .env | grep -v '^#' | xargs) && python3 slack_knowledge_extractor_simple.py"
else
    echo "❌ Failed to install cron job"
    exit 1
fi




