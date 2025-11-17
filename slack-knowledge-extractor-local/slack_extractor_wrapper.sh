#!/bin/bash
# Slack Knowledge Extractor - Cron Job Wrapper
# This script wraps the Python extraction script for cron execution
# Ensures proper environment and error handling

# Set script directory
SCRIPT_DIR="/opt/slack-knowledge-extractor"
LOG_DIR="/var/log"
PYTHON_SCRIPT="$SCRIPT_DIR/slack_knowledge_extractor.py"

# Environment file
ENV_FILE="$SCRIPT_DIR/.env"

# Log file for this wrapper
WRAPPER_LOG="$LOG_DIR/slack-extractor-wrapper.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$WRAPPER_LOG"
}

# Function to check if script is already running
check_running() {
    local pid_file="/tmp/slack_extractor.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "ERROR: Slack extractor is already running (PID: $pid)"
            return 1
        else
            rm -f "$pid_file"
        fi
    fi
    
    # Create PID file
    echo $$ > "$pid_file"
    return 0
}

# Function to cleanup on exit
cleanup() {
    rm -f /tmp/slack_extractor.pid
    log "Cleanup completed"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main execution
main() {
    log "Starting Slack Knowledge Extractor wrapper"
    
    # Check if already running
    if ! check_running; then
        exit 1
    fi
    
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
    
    # Load environment variables
    log "Loading environment variables from $ENV_FILE"
    set -a
    source "$ENV_FILE"
    set +a
    
    # Check required environment variables
    required_vars=("SLACK_BOT_TOKEN" "SUPABASE_URL" "SUPABASE_ANON_KEY" "SUPABASE_EMAIL" "SUPABASE_PASSWORD")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log "ERROR: Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Change to script directory
    cd "$SCRIPT_DIR" || {
        log "ERROR: Cannot change to directory $SCRIPT_DIR"
        exit 1
    }
    
    # Run the Python script
    log "Executing Python extraction script"
    python3 "$PYTHON_SCRIPT"
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log "Slack Knowledge Extractor completed successfully"
    else
        log "ERROR: Slack Knowledge Extractor failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
