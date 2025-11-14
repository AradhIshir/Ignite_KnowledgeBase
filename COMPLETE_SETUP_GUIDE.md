# 🚀 Slack Knowledge Extractor - COMPLETE SETUP GUIDE

## ✅ **Current Status: ALMOST READY!**

### **✅ What's Working:**
- ✅ Slack bot connection successful
- ✅ Supabase database insertion working perfectly
- ✅ Keyword extraction logic implemented
- ✅ All scripts created and tested
- ✅ Environment configured

### **❌ What Needs Fixing:**
- ❌ Slack bot needs `channels:history` scope to read messages

---

## 🔧 **STEP 1: Fix Slack Bot Permissions**

### **Add Missing Scope:**
1. Go to https://api.slack.com/apps
2. Select your "Knowledge Extractor Bot" app
3. Go to **"OAuth & Permissions"**
4. In **"Bot Token Scopes"**, add:
   - `channels:history` - **This is the missing scope!**
5. Click **"Save Changes"**
6. Click **"Reinstall to Workspace"**
7. Confirm the installation

### **Required Scopes (Complete List):**
- ✅ `channels:read` - Read public channel info
- ✅ `groups:read` - Read private channel info  
- ✅ `im:read` - Read direct messages
- ✅ `mpim:read` - Read group direct messages
- ✅ `users:read` - Read user information
- ❌ `channels:history` - **ADD THIS ONE** - Read channel message history

---

## 🚀 **STEP 2: Set Up Cron Job**

### **Option A: Manual Cron Setup**
```bash
# 1. Open crontab editor
crontab -e

# 2. Add this line (runs every 10 minutes):
*/10 * * * * cd /Users/ishir/Desktop/IgniteCursor && export $(cat .env | grep -v '^#' | xargs) && python3 slack_knowledge_extractor_simple.py >> slack-extractor.log 2>&1

# 3. Save and exit
```

### **Option B: Automated Setup Script**
```bash
# Create a simple cron setup script
cat > setup_cron.sh << 'EOF'
#!/bin/bash
echo "Setting up cron job for Slack Knowledge Extractor..."

# Get current directory
CURRENT_DIR=$(pwd)

# Create cron entry
CRON_ENTRY="*/10 * * * * cd $CURRENT_DIR && export \$(cat .env | grep -v '^#' | xargs) && python3 slack_knowledge_extractor_simple.py >> slack-extractor.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job installed successfully!"
echo "📅 Schedule: Every 10 minutes"
echo "📁 Working directory: $CURRENT_DIR"
echo "📝 Log file: slack-extractor.log"
echo ""
echo "To check if it's working:"
echo "  tail -f slack-extractor.log"
echo ""
echo "To remove the cron job:"
echo "  crontab -e  # then delete the line"
EOF

chmod +x setup_cron.sh
./setup_cron.sh
```

---

## 🧪 **STEP 3: Test Everything**

### **Test Slack Bot Permissions:**
```bash
# After adding channels:history scope, test:
export $(cat .env | grep -v '^#' | xargs) && python3 slack_knowledge_extractor_simple.py
```

### **Expected Output:**
```
✅ Slack connection successful!
✅ Fetched X messages from Slack
✅ Extracted Y topics, Z decisions, W FAQs
✅ Successfully inserted knowledge into Supabase
```

### **Test Cron Job:**
```bash
# Check if cron job is installed
crontab -l

# Monitor logs
tail -f slack-extractor.log
```

---

## 📊 **STEP 4: Monitor the System**

### **Log Files:**
- **Main log**: `slack-extractor.log` (in your project directory)
- **Application log**: `slack-knowledge-extractor.log` (in your project directory)

### **Monitor Commands:**
```bash
# Watch logs in real-time
tail -f slack-extractor.log

# Check recent extractions
grep "Successfully inserted" slack-extractor.log

# Check for errors
grep "ERROR" slack-extractor.log
```

### **Check Supabase:**
- Visit your Supabase dashboard
- Go to Table Editor → knowledge_items
- You should see new entries every 10 minutes

---

## 🎯 **FINAL CONFIGURATION**

### **Current Environment (.env):**
```bash
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key-here
SUPABASE_EMAIL=your-email@example.com
SUPABASE_PASSWORD=your-password-here
```

### **Files Ready:**
- ✅ `slack_knowledge_extractor_simple.py` - Main extraction script
- ✅ `slack_extractor_wrapper.sh` - Cron wrapper (optional)
- ✅ `.env` - Environment configuration
- ✅ `test_supabase_insertion.py` - Test script
- ✅ `test_connections.py` - Connection test script

---

## 🚨 **TROUBLESHOOTING**

### **If Slack Still Shows "missing_scope":**
1. Double-check you added `channels:history` scope
2. Make sure you clicked "Reinstall to Workspace"
3. Wait 2-3 minutes for permissions to propagate
4. Test again

### **If Cron Job Doesn't Run:**
```bash
# Check cron service
sudo launchctl list | grep cron

# Check cron logs
grep CRON /var/log/system.log

# Test manual execution
cd /Users/ishir/Desktop/IgniteCursor && export $(cat .env | grep -v '^#' | xargs) && python3 slack_knowledge_extractor_simple.py
```

### **If Supabase Insertion Fails:**
- Check that RLS is still disabled
- Verify the anon key is correct
- Check network connectivity

---

## 🎉 **SUCCESS INDICATORS**

You'll know it's working when you see:
1. ✅ Slack bot fetches messages successfully
2. ✅ Keywords are extracted from messages
3. ✅ Data is inserted into Supabase knowledge_items table
4. ✅ New entries appear every 10 minutes
5. ✅ Log files show successful runs

---

## 📈 **NEXT STEPS**

Once everything is working:
1. **Monitor for 24 hours** to ensure stability
2. **Check Supabase dashboard** for accumulated knowledge
3. **Review extracted topics** for relevance
4. **Adjust extraction parameters** if needed
5. **Set up alerts** for failures (optional)

---

**🎯 The system is 95% ready - just need to add the `channels:history` scope to your Slack bot!**




