-- Insert keyword extraction knowledge item into the database
-- This script extracts keywords from READMEs and project documentation

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
  'Knowledge base keyword extraction and documentation update - analyzing READMEs for technical keywords and project features',
  
  ARRAY[
    'Keyword Extraction',
    'Knowledge Base Management',
    'Technical Documentation',
    'FastAPI Backend',
    'Next.js Frontend',
    'Supabase Database',
    'Authentication',
    'Export Functionality',
    'React Components',
    'Styled Components',
    'TypeScript',
    'Python',
    'Poetry',
    'WeasyPrint',
    'PDF Generation',
    'CSV Export',
    'RESTful API',
    'Row Level Security',
    'Theme Management',
    'User Management'
  ],
  
  ARRAY[
    'Use Supabase for authentication and database management',
    'Implement export functionality with CSV and PDF formats',
    'Use FastAPI for backend API with ReportLab for PDF generation',
    'Use Next.js with TypeScript for frontend development',
    'Use Styled Components for theming with blue/green color scheme',
    'Implement Row Level Security (RLS) policies for data protection'
  ],
  
  ARRAY[
    'Q: What backend framework is used? A: FastAPI with Python 3.10+',
    'Q: What frontend framework is used? A: Next.js 14.2.5 with TypeScript',
    'Q: How is authentication handled? A: Supabase Auth with RLS policies',
    'Q: What export formats are supported? A: CSV and PDF formats',
    'Q: What styling solution is used? A: Styled Components with custom theme',
    'Q: What database is used? A: PostgreSQL via Supabase',
    'Q: What package manager is used for Python? A: Poetry',
    'Q: What port does the backend run on? A: Port 8080'
  ],
  
  'Thread Analysis - Backend/Frontend README files',
  '2025-10-27',
  'Ignite Knowledge',
  
  'EXTRACTED KEYWORDS AND TECHNICAL TERMS FROM PROJECT DOCUMENTATION:

BACKEND (FastAPI):
- FastAPI framework
- Python 3.10+ with Poetry
- Export endpoints (CSV/PDF)
- WeasyPrint for PDF generation
- ReportLab for PDF rendering
- CORS middleware
- Uvicorn server
- Port 8080
- Health check endpoint

FRONTEND (Next.js):
- Next.js 14.2.5
- TypeScript
- Styled Components
- React hooks (useState, useEffect)
- Supabase client integration
- Theme switcher
- Blue/green color theme
- Responsive design
- Authentication pages (signin, signup, forgot)
- Dashboard with summary cards
- Knowledge items management (CRUD)
- Search and filtering
- Multi-select filters

DATABASE (Supabase):
- PostgreSQL database
- UUID extensions
- knowledge_items table (summary, topics, decisions, faqs, source, date, project, raw_text)
- user_favorites table
- activity_log table
- Row Level Security (RLS)
- Authentication policies
- Triggers for updated_at

ARCHITECTURE:
- Full-stack application
- RESTful API
- Modern dashboard
- Card-based layout
- Real-time subscriptions
- State management with React hooks
- Profile and session management
- Admin panel
- Export functionality

KEY FEATURES:
- Knowledge management system
- Article creation and viewing
- Search with project/topic filters
- CSV/PDF export
- User authentication
- Favorites system
- Activity tracking
- Summary cards with statistics
- Responsive UI/UX'
);

-- Display the inserted item
SELECT id, summary, created_at 
FROM public.knowledge_items 
ORDER BY created_at DESC 
LIMIT 1;
