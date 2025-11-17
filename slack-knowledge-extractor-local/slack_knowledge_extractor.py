#!/usr/bin/env python3
"""
Slack Knowledge Extraction Agent
Automated script to fetch Slack messages, extract keywords, and insert into Supabase knowledge base.
Designed to run as a cron job every 10 minutes.
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/slack-knowledge-extractor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SlackMessage:
    """Data class for Slack message structure"""
    text: str
    user: str
    channel: str
    timestamp: str
    thread_ts: str = None

@dataclass
class ExtractedKnowledge:
    """Data class for extracted knowledge item"""
    summary: str
    topics: List[str]
    decisions: List[str]
    faqs: List[str]
    source: str
    date: str
    project: str
    raw_text: str

class SlackKnowledgeExtractor:
    """Main class for Slack knowledge extraction workflow"""
    
    def __init__(self):
        """Initialize with environment variables"""
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_email = os.getenv('SUPABASE_EMAIL')
        self.supabase_password = os.getenv('SUPABASE_PASSWORD')
        
        # Validate required environment variables
        required_vars = [
            'SLACK_BOT_TOKEN', 'SUPABASE_URL', 'SUPABASE_ANON_KEY',
            'SUPABASE_EMAIL', 'SUPABASE_PASSWORD'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            sys.exit(1)
        
        # Slack API configuration
        self.slack_headers = {
            'Authorization': f'Bearer {self.slack_token}',
            'Content-Type': 'application/json'
        }
        
        # Supabase configuration
        self.supabase_headers = {
            'apikey': self.supabase_key,
            'Content-Type': 'application/json'
        }
        
        # Access token for Supabase (will be obtained during authentication)
        self.supabase_access_token = None
        
        logger.info("SlackKnowledgeExtractor initialized successfully")
    
    def authenticate_supabase(self) -> bool:
        """Authenticate with Supabase and get access token"""
        try:
            logger.info("Authenticating with Supabase...")
            
            # Try to sign in
            auth_url = f"{self.supabase_url}/auth/v1/token?grant_type=password"
            auth_data = {
                "email": self.supabase_email,
                "password": self.supabase_password
            }
            
            response = requests.post(auth_url, headers=self.supabase_headers, json=auth_data)
            
            if response.status_code == 200:
                auth_result = response.json()
                self.supabase_access_token = auth_result.get('access_token')
                
                if self.supabase_access_token:
                    logger.info("✅ Successfully authenticated with Supabase")
                    return True
                else:
                    logger.error("No access token received from Supabase")
                    return False
            else:
                logger.error(f"Supabase authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error during Supabase authentication: {str(e)}")
            return False
    
    def fetch_slack_messages(self, hours_back: int = 24) -> List[SlackMessage]:
        """Fetch Slack messages from the last N hours"""
        try:
            logger.info(f"Fetching Slack messages from the last {hours_back} hours...")
            
            # Calculate timestamp for N hours ago
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            cutoff_timestamp = int(cutoff_time.timestamp())
            
            messages = []
            
            # Get list of channels
            channels_url = "https://slack.com/api/conversations.list"
            channels_response = requests.get(channels_url, headers=self.slack_headers)
            
            if channels_response.status_code != 200:
                logger.error(f"Failed to fetch channels: {channels_response.text}")
                return messages
            
            channels_data = channels_response.json()
            if not channels_data.get('ok'):
                logger.error(f"Slack API error: {channels_data.get('error')}")
                return messages
            
            # Fetch messages from each channel
            for channel in channels_data.get('channels', []):
                channel_id = channel['id']
                channel_name = channel['name']
                
                # Skip archived channels
                if channel.get('is_archived', False):
                    continue
                
                logger.info(f"Fetching messages from channel: {channel_name}")
                
                # Get channel history
                history_url = "https://slack.com/api/conversations.history"
                history_params = {
                    'channel': channel_id,
                    'oldest': str(cutoff_timestamp),
                    'limit': 100
                }
                
                history_response = requests.get(history_url, headers=self.slack_headers, params=history_params)
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    
                    if history_data.get('ok'):
                        for msg in history_data.get('messages', []):
                            # Skip bot messages and system messages
                            if msg.get('bot_id') or msg.get('subtype'):
                                continue
                            
                            # Skip messages without text
                            if not msg.get('text'):
                                continue
                            
                            slack_msg = SlackMessage(
                                text=msg['text'],
                                user=msg.get('user', 'unknown'),
                                channel=channel_name,
                                timestamp=msg['ts'],
                                thread_ts=msg.get('thread_ts')
                            )
                            messages.append(slack_msg)
                    else:
                        logger.warning(f"Failed to fetch history for channel {channel_name}: {history_data.get('error')}")
            
            logger.info(f"Fetched {len(messages)} messages from Slack")
            return messages
            
        except Exception as e:
            logger.error(f"Error fetching Slack messages: {str(e)}")
            return []
    
    def extract_keywords_from_messages(self, messages: List[SlackMessage]) -> ExtractedKnowledge:
        """Extract keywords and knowledge from Slack messages"""
        try:
            logger.info("Extracting keywords and knowledge from messages...")
            
            # Combine all message texts
            all_text = " ".join([msg.text for msg in messages])
            
            # Extract topics/keywords using regex patterns
            topics = self._extract_topics(all_text)
            
            # Extract decisions
            decisions = self._extract_decisions(all_text)
            
            # Extract FAQs
            faqs = self._extract_faqs(all_text)
            
            # Create summary
            summary = self._create_summary(messages, topics)
            
            # Create raw text
            raw_text = self._create_raw_text(messages)
            
            knowledge = ExtractedKnowledge(
                summary=summary,
                topics=topics,
                decisions=decisions,
                faqs=faqs,
                source="Slack Integration - Automated Extraction",
                date=datetime.now().strftime("%Y-%m-%d"),
                project="Team Knowledge Base",
                raw_text=raw_text
            )
            
            logger.info(f"Extracted {len(topics)} topics, {len(decisions)} decisions, {len(faqs)} FAQs")
            return knowledge
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return None
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics/keywords from text"""
        # Common technology keywords
        tech_keywords = [
            'Next.js', 'React', 'TypeScript', 'JavaScript', 'Python', 'FastAPI',
            'Supabase', 'PostgreSQL', 'Node.js', 'API', 'Database', 'Frontend',
            'Backend', 'Authentication', 'Security', 'Deployment', 'Docker',
            'AWS', 'Azure', 'Git', 'GitHub', 'CI/CD', 'Testing', 'Debugging'
        ]
        
        # Project management keywords
        pm_keywords = [
            'Sprint', 'Planning', 'Review', 'Retrospective', 'Backlog', 'Epic',
            'Story', 'Task', 'Bug', 'Feature', 'Release', 'Deployment',
            'Documentation', 'Meeting', 'Decision', 'Action Item'
        ]
        
        # Business keywords
        business_keywords = [
            'Customer', 'User', 'Product', 'Feature', 'Revenue', 'Growth',
            'Strategy', 'Goal', 'Objective', 'KPI', 'Metric', 'Analytics'
        ]
        
        all_keywords = tech_keywords + pm_keywords + business_keywords
        
        # Find keywords in text (case-insensitive)
        found_topics = []
        text_lower = text.lower()
        
        for keyword in all_keywords:
            if keyword.lower() in text_lower:
                found_topics.append(keyword)
        
        # Remove duplicates and limit to top 20
        return list(set(found_topics))[:20]
    
    def _extract_decisions(self, text: str) -> List[str]:
        """Extract decisions from text"""
        decisions = []
        
        # Look for decision patterns
        decision_patterns = [
            r'(?:decided|decision|agreed|concluded|resolved).*?(?:to|that|on|we will)',
            r'(?:we will|going to|plan to|will implement|will use)',
            r'(?:chose|selected|picked|opted for)',
            r'(?:approved|accepted|confirmed)'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
                
            for pattern in decision_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    # Clean up the decision
                    decision = sentence[:200] + "..." if len(sentence) > 200 else sentence
                    decisions.append(decision)
                    break
        
        return decisions[:10]  # Limit to 10 decisions
    
    def _extract_faqs(self, text: str) -> List[str]:
        """Extract potential FAQs from text"""
        faqs = []
        
        # Look for question patterns
        question_patterns = [
            r'(?:how do|how to|how can|how will|how should)',
            r'(?:what is|what are|what does|what will)',
            r'(?:why|when|where|who)',
            r'(?:can we|should we|will we|do we)'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15:  # Skip very short sentences
                continue
                
            for pattern in question_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    # Format as FAQ
                    faq = f"Q: {sentence} A: [Answer extracted from context]"
                    faqs.append(faq)
                    break
        
        return faqs[:8]  # Limit to 8 FAQs
    
    def _create_summary(self, messages: List[SlackMessage], topics: List[str]) -> str:
        """Create a summary of the extracted knowledge"""
        message_count = len(messages)
        channel_count = len(set(msg.channel for msg in messages))
        topic_count = len(topics)
        
        summary = f"Slack Knowledge Extraction - {message_count} messages from {channel_count} channels, {topic_count} topics identified"
        
        if topics:
            top_topics = topics[:5]
            summary += f". Key topics: {', '.join(top_topics)}"
        
        return summary
    
    def _create_raw_text(self, messages: List[SlackMessage]) -> str:
        """Create raw text from messages"""
        raw_text = "SLACK MESSAGES EXTRACTION\n\n"
        
        # Group messages by channel
        channels = {}
        for msg in messages:
            if msg.channel not in channels:
                channels[msg.channel] = []
            channels[msg.channel].append(msg)
        
        for channel, msgs in channels.items():
            raw_text += f"CHANNEL: #{channel}\n"
            raw_text += "=" * 50 + "\n"
            
            for msg in msgs[:10]:  # Limit to 10 messages per channel
                timestamp = datetime.fromtimestamp(float(msg.timestamp)).strftime("%Y-%m-%d %H:%M")
                raw_text += f"[{timestamp}] {msg.user}: {msg.text}\n"
            
            raw_text += "\n"
        
        return raw_text
    
    def insert_into_supabase(self, knowledge: ExtractedKnowledge) -> bool:
        """Insert extracted knowledge into Supabase"""
        try:
            logger.info("Inserting knowledge into Supabase...")
            
            if not self.supabase_access_token:
                logger.error("No Supabase access token available")
                return False
            
            # Prepare data for insertion
            insert_data = {
                "summary": knowledge.summary,
                "topics": knowledge.topics,
                "decisions": knowledge.decisions,
                "faqs": knowledge.faqs,
                "source": knowledge.source,
                "date": knowledge.date,
                "project": knowledge.project,
                "raw_text": knowledge.raw_text
            }
            
            # Insert into Supabase
            insert_url = f"{self.supabase_url}/rest/v1/knowledge_items"
            insert_headers = {
                **self.supabase_headers,
                "Authorization": f"Bearer {self.supabase_access_token}",
                "Prefer": "return=representation"
            }
            
            response = requests.post(insert_url, headers=insert_headers, json=insert_data)
            
            if response.status_code in [200, 201]:
                logger.info("✅ Successfully inserted knowledge into Supabase")
                logger.info(f"Inserted data: {json.dumps(response.json(), indent=2)}")
                return True
            else:
                logger.error(f"Failed to insert into Supabase: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting into Supabase: {str(e)}")
            return False
    
    def run_extraction_workflow(self) -> bool:
        """Run the complete extraction workflow"""
        try:
            logger.info("=" * 60)
            logger.info("Starting Slack Knowledge Extraction Workflow")
            logger.info("=" * 60)
            
            # Step 1: Authenticate with Supabase
            if not self.authenticate_supabase():
                logger.error("Failed to authenticate with Supabase")
                return False
            
            # Step 2: Fetch Slack messages
            messages = self.fetch_slack_messages(hours_back=24)
            if not messages:
                logger.warning("No messages found to process")
                return True  # Not an error, just no data
            
            # Step 3: Extract knowledge
            knowledge = self.extract_keywords_from_messages(messages)
            if not knowledge:
                logger.error("Failed to extract knowledge from messages")
                return False
            
            # Step 4: Insert into Supabase
            if not self.insert_into_supabase(knowledge):
                logger.error("Failed to insert knowledge into Supabase")
                return False
            
            logger.info("=" * 60)
            logger.info("✅ Slack Knowledge Extraction Workflow Completed Successfully")
            logger.info("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"Error in extraction workflow: {str(e)}")
            return False

def main():
    """Main entry point"""
    try:
        extractor = SlackKnowledgeExtractor()
        success = extractor.run_extraction_workflow()
        
        if success:
            logger.info("Extraction completed successfully")
            sys.exit(0)
        else:
            logger.error("Extraction failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
