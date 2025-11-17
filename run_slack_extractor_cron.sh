#!/bin/bash
# Slack Knowledge Extractor - Cron Job Wrapper
# This script wraps the Python extraction script for cron execution

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Environment file
ENV_FILE="$SCRIPT_DIR/slack-extractor.env"

# Log file
LOG_FILE="$SCRIPT_DIR/slack-extractor.log"

# Python script
PYTHON_SCRIPT="$SCRIPT_DIR/slack_knowledge_extractor_simple.py"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log "ERROR: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    log "ERROR: Environment file not found at $ENV_FILE"
    exit 1
fi

# Load environment variables from the env file
log "Loading environment variables from $ENV_FILE"
set -a
source "$ENV_FILE"
set +a

# Check required environment variables
if [ -z "$SLACK_BOT_TOKEN" ]; then
    log "ERROR: SLACK_BOT_TOKEN is not set"
    exit 1
fi

if [ -z "$SUPABASE_URL" ]; then
    log "ERROR: SUPABASE_URL is not set"
    exit 1
fi

if [ -z "$SUPABASE_ANON_KEY" ]; then
    log "ERROR: SUPABASE_ANON_KEY is not set"
    exit 1
fi

# Run the Python script
log "Starting Slack Knowledge Extractor"
python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log "Slack Knowledge Extractor completed successfully"
else
    log "ERROR: Slack Knowledge Extractor failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE

