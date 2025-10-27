-- SQL script to add knowledge item from Slack thread
-- This can be run in the Supabase SQL Editor

INSERT INTO public.knowledge_items (
  summary,
  topics,
  decisions,
  faqs,
  source,
  date,
  project,
  raw_text
) VALUES (
  'Automated Keyword Extraction from Slack Threads for Knowledge Base',
  ARRAY[
    'keyword extraction',
    'automation',
    'knowledge base',
    'Slack integration',
    'repository setup',
    'AI processing'
  ],
  ARRAY[
    'Implement automated keyword extraction from Slack threads',
    'Set up repository integration for processing',
    'Update knowledge base automatically from thread content'
  ],
  ARRAY[
    'Q: How to extract keywords from Slack threads? A: Use AI/NLP to analyze thread content and identify key topics',
    'Q: What repository is needed? A: The Ignite Knowledge application repository for knowledge base updates'
  ],
  'Slack Thread',
  '2025-10-27',
  'Ignite Knowledge',
  '[10/27/2025, 5:50:01 AM] aradhana goyal: @Cursor extract main keywords from this thread and update the knowledge base
[10/27/2025, 5:50:05 AM] Cursor: Repository setup required
[10/27/2025, 6:31:51 AM] aradhana goyal: @Cursor I have given you the repo'
);
