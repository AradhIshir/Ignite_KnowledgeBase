# Slack Knowledge Extractor - Complete Setup Guide

## Overview

This system automatically extracts keywords and knowledge from your Slack workspace and inserts them into your Supabase knowledge base every 10 minutes. It's designed to run unattended on a Linux server with cron jobs.

## System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **Memory**: Minimum 512MB RAM
- **Storage**: 100MB free space
- **Network**: Internet access for Slack and Supabase APIs

## Prerequisites

### 1. Slack Bot Setup

1. **Create a Slack App**:
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name: "Knowledge Extractor Bot"
   - Select your workspace

2. **Configure Bot Permissions**:
   - Go to "OAuth & Permissions"
   - Add these Bot Token Scopes:
     - `channels:read` - Read public channel messages
     - `groups:read` - Read private channel messages
     - `im:read` - Read direct messages
     - `mpim:read` - Read group direct messages
     - `users:read` - Read user information

3. **Install App to Workspace**:
   - Click "Install to Workspace"
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 2. Supabase Setup

1. **Create Supabase User** (if not exists):
   - Go to your Supabase dashboard
   - Navigate to Authentication → Users
   - Create a new user or use existing credentials

2. **Verify Database Schema**:
   - Ensure `knowledge_items` table exists
   - Verify RLS policies allow authenticated inserts

## Installation

### Quick Installation (Recommended)

1. **Download and run the installer**:
   ```bash
   # Download the installation files
   wget https://your-server.com/slack_knowledge_extractor.py
   wget https://your-server.com/slack_extractor_wrapper.sh
   wget https://your-server.com/install.sh
   wget https://your-server.com/env.example
   
   # Make installer executable and run
   chmod +x install.sh
   sudo ./install.sh
   ```

### Manual Installation

1. **Create installation directory**:
   ```bash
   sudo mkdir -p /opt/slack-knowledge-extractor
   sudo useradd -r -s /bin/bash -d /opt/slack-knowledge-extractor slack-extractor
   sudo chown -R slack-extractor:slack-extractor /opt/slack-knowledge-extractor
   ```

2. **Install Python dependencies**:
   ```bash
   sudo pip3 install requests python-dateutil
   ```

3. **Copy application files**:
   ```bash
   sudo cp slack_knowledge_extractor.py /opt/slack-knowledge-extractor/
   sudo cp slack_extractor_wrapper.sh /opt/slack-knowledge-extractor/
   sudo cp env.example /opt/slack-knowledge-extractor/.env.example
   
   sudo chmod +x /opt/slack-knowledge-extractor/slack_knowledge_extractor.py
   sudo chmod +x /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh
   sudo chown -R slack-extractor:slack-extractor /opt/slack-knowledge-extractor
   ```

4. **Setup environment**:
   ```bash
   sudo cp /opt/slack-knowledge-extractor/.env.example /opt/slack-knowledge-extractor/.env
   sudo chmod 600 /opt/slack-knowledge-extractor/.env
   sudo chown slack-extractor:slack-extractor /opt/slack-knowledge-extractor/.env
   ```

5. **Configure cron job**:
   ```bash
   sudo crontab -e
   # Add this line:
   */10 * * * * /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh >> /var/log/slack-extractor-cron.log 2>&1
   ```

## Configuration

### Environment Variables

Edit the environment file:
```bash
sudo nano /opt/slack-knowledge-extractor/.env
```

Required variables:
```bash
# Slack Bot Token (from Slack App setup)
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token-here

# Supabase Configuration
SUPABASE_URL=https://wwmqodqqqrffxdvgisrd.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3bXFvZHFxcXJmZnhkdmdpc3JkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNzkwODIsImV4cCI6MjA3Njg1NTA4Mn0.Af0VXHqBc-rEHy8jbcXcCakpPFfyE_B_koOAiAS_ZcI

# Supabase Authentication (for inserting data)
SUPABASE_EMAIL=your-supabase-user@example.com
SUPABASE_PASSWORD=your-supabase-password
```

Optional variables:
```bash
# Customize extraction behavior
EXTRACTION_HOURS_BACK=24          # How many hours back to fetch messages
MAX_MESSAGES_PER_CHANNEL=100      # Limit messages per channel
MAX_TOPICS=20                     # Maximum topics to extract
MAX_DECISIONS=10                  # Maximum decisions to extract
MAX_FAQS=8                        # Maximum FAQs to extract

# Channel filtering
INCLUDE_CHANNELS=                 # Specific channels to include (comma-separated)
EXCLUDE_CHANNELS=general,random   # Channels to exclude (comma-separated)
```

## Testing

### Test the Installation

1. **Run a test extraction**:
   ```bash
   sudo -u slack-extractor /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh
   ```

2. **Check logs**:
   ```bash
   tail -f /var/log/slack-knowledge-extractor.log
   ```

3. **Verify Supabase insertion**:
   - Check your Supabase dashboard
   - Look for new entries in `knowledge_items` table
   - Verify the data matches your Slack messages

### Troubleshooting

**Common Issues**:

1. **Permission Denied**:
   ```bash
   sudo chown -R slack-extractor:slack-extractor /opt/slack-knowledge-extractor
   sudo chmod +x /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh
   ```

2. **Slack API Errors**:
   - Verify bot token is correct
   - Check bot permissions in Slack app settings
   - Ensure bot is installed in your workspace

3. **Supabase Authentication Errors**:
   - Verify email/password are correct
   - Check if user exists in Supabase
   - Verify RLS policies allow inserts

4. **Cron Job Not Running**:
   ```bash
   # Check cron service
   sudo systemctl status cron
   
   # Check cron logs
   sudo tail -f /var/log/syslog | grep CRON
   
   # Test cron job manually
   sudo -u slack-extractor /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh
   ```

## Monitoring

### Log Files

- **Main log**: `/var/log/slack-knowledge-extractor.log`
- **Cron log**: `/var/log/slack-extractor-cron.log`
- **Wrapper log**: `/var/log/slack-extractor-wrapper.log`

### Monitoring Commands

```bash
# Monitor real-time logs
tail -f /var/log/slack-knowledge-extractor.log

# Check recent cron executions
grep "slack_extractor_wrapper" /var/log/syslog | tail -10

# Check system resources
ps aux | grep slack_extractor
```

## Cron Schedule

The system runs every 10 minutes with this cron expression:
```bash
*/10 * * * * /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh >> /var/log/slack-extractor-cron.log 2>&1
```

### Customizing Schedule

To change the frequency, edit the cron entry:
```bash
# Every 5 minutes
*/5 * * * * /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh >> /var/log/slack-extractor-cron.log 2>&1

# Every hour
0 * * * * /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh >> /var/log/slack-extractor-cron.log 2>&1

# Every day at 9 AM
0 9 * * * /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh >> /var/log/slack-extractor-cron.log 2>&1
```

## Security Considerations

1. **Environment File**: Keep `.env` file secure (600 permissions)
2. **Service User**: Runs as non-root user (`slack-extractor`)
3. **Log Rotation**: Consider setting up log rotation for large log files
4. **Network Security**: Ensure server has proper firewall rules
5. **Token Security**: Never commit Slack tokens to version control

## Maintenance

### Regular Tasks

1. **Monitor disk space**:
   ```bash
   df -h /var/log
   ```

2. **Rotate logs** (if needed):
   ```bash
   sudo logrotate -f /etc/logrotate.conf
   ```

3. **Update dependencies**:
   ```bash
   sudo pip3 install --upgrade requests python-dateutil
   ```

### Updating the Script

1. **Backup current version**:
   ```bash
   sudo cp /opt/slack-knowledge-extractor/slack_knowledge_extractor.py /opt/slack-knowledge-extractor/slack_knowledge_extractor.py.backup
   ```

2. **Update script**:
   ```bash
   sudo cp new_slack_knowledge_extractor.py /opt/slack-knowledge-extractor/slack_knowledge_extractor.py
   sudo chown slack-extractor:slack-extractor /opt/slack-knowledge-extractor/slack_knowledge_extractor.py
   ```

3. **Test update**:
   ```bash
   sudo -u slack-extractor /opt/slack-knowledge-extractor/slack_extractor_wrapper.sh
   ```

## Support

For issues or questions:
1. Check the log files first
2. Verify environment configuration
3. Test Slack and Supabase API access manually
4. Review this documentation

## File Structure

After installation, your system will have:
```
/opt/slack-knowledge-extractor/
├── slack_knowledge_extractor.py    # Main Python script
├── slack_extractor_wrapper.sh      # Cron wrapper script
├── .env                            # Environment configuration
└── .env.example                     # Environment template

/var/log/
├── slack-knowledge-extractor.log    # Main application log
├── slack-extractor-cron.log        # Cron execution log
└── slack-extractor-wrapper.log     # Wrapper script log
```

This system will automatically extract knowledge from your Slack workspace and populate your Supabase knowledge base every 10 minutes, running completely unattended.
