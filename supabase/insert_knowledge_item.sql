-- Insert knowledge item for the development thread
-- Run this in Supabase SQL Editor

INSERT INTO public.knowledge_items (
  summary,
  topics,
  decisions,
  faqs,
  source,
  date,
  project,
  raw_text,
  created_at,
  updated_at
) VALUES (
  'Ignite Knowledge - Team Knowledge Base Application Development Thread',
  
  -- Topics (27 keywords extracted from README and git history)
  ARRAY[
    'Next.js',
    'React',
    'TypeScript',
    'Styled Components',
    'FastAPI',
    'Python',
    'Poetry',
    'Uvicorn',
    'Supabase',
    'PostgreSQL',
    'Row Level Security',
    'Authentication',
    'Knowledge Management',
    'Dashboard',
    'Search & Filtering',
    'Data Export',
    'CSV Export',
    'PDF Export',
    'WeasyPrint',
    'Modern Design',
    'Responsive Design',
    'Theme Switcher',
    'Card-based Layout',
    'Full-stack Application',
    'REST API',
    'Real-time Subscriptions',
    'CORS'
  ],
  
  -- Decisions
  ARRAY[
    'Built with Next.js 14.2.5 and TypeScript for frontend',
    'FastAPI backend with Python 3.10+ for export functionality',
    'Supabase for authentication and PostgreSQL database',
    'Styled Components for modern UI with blue/green theme',
    'CSV and PDF export capabilities using WeasyPrint',
    'Row-level security policies for data protection'
  ],
  
  -- FAQs
  ARRAY[
    'Q: What tech stack is used? A: Next.js, FastAPI, Supabase, TypeScript',
    'Q: What is the main purpose? A: Team knowledge management with search, filtering, and export',
    'Q: What export formats are supported? A: CSV and PDF',
    'Q: How is authentication handled? A: Supabase Auth with row-level security',
    'Q: Is it responsive? A: Yes, works on all screen sizes'
  ],
  
  -- Source
  'Git Development Thread - Branch: cursor/extract-keywords-and-update-knowledge-base-2150',
  
  -- Date
  '2025-10-27',
  
  -- Project
  'Ignite Knowledge',
  
  -- Raw text
  'Ignite Knowledge - Team Knowledge Base Application

This is a comprehensive development thread documenting the creation of a modern, 
full-stack knowledge management application.

Key Features Developed:
- Authentication System with Supabase Auth
- Modern Dashboard with KnowledgeHub-style interface
- Knowledge article creation and management
- Real-time search with project and topic filters
- CSV export functionality
- Responsive design with styled components

Architecture:
- Frontend: Next.js 14.2.5 with TypeScript
- Backend: FastAPI with Python 3.10+
- Database: Supabase (PostgreSQL)
- Styling: Styled Components with custom theme

Git Commits:
1. Initial commit: Ignite Knowledge - Team Knowledge Base Application
2. Fix build issues for deployment
3. Initial commit

The application is production-ready with complete authentication, knowledge management,
search/filtering, and data export capabilities.',
  
  -- Timestamps
  NOW(),
  NOW()
);

-- Verify the insertion
SELECT 
  id,
  summary,
  array_length(topics, 1) as topic_count,
  array_length(decisions, 1) as decision_count,
  array_length(faqs, 1) as faq_count,
  project,
  date,
  created_at
FROM public.knowledge_items
WHERE summary LIKE '%Development Thread%'
ORDER BY created_at DESC
LIMIT 1;
