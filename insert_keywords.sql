-- SQL INSERT Statement for Extracted Keywords
-- Run this in Supabase SQL Editor or via authenticated API call
-- Date: 2025-10-27
-- Project: Ignite Knowledge

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
  'Project Keywords and Technical Stack Documentation - Extracted main keywords from Ignite Knowledge project covering full-stack architecture, technologies, features, and development workflow',
  
  -- Topics Array
  ARRAY[
    'Next.js',
    'TypeScript',
    'React',
    'Styled Components',
    'FastAPI',
    'Python',
    'Poetry',
    'Supabase',
    'PostgreSQL',
    'Authentication',
    'Knowledge Management',
    'Full-Stack Development',
    'RESTful API',
    'Row-Level Security',
    'Real-time Subscriptions',
    'CSV Export',
    'PDF Export',
    'Search & Filtering',
    'Dashboard',
    'Responsive Design'
  ],
  
  -- Decisions Array
  ARRAY[
    'Use Next.js 14.2.5 for frontend framework',
    'Implement FastAPI for backend services',
    'Choose Supabase for database and authentication',
    'Use Styled Components for styling solution',
    'Implement Poetry for Python dependency management',
    'Enable CORS for cross-origin requests',
    'Use Row-Level Security policies for data protection',
    'Implement real-time subscriptions for live updates',
    'Create modular component-based architecture',
    'Support CSV and PDF export formats'
  ],
  
  -- FAQs Array
  ARRAY[
    'Q: What technologies are used? A: Next.js, FastAPI, Supabase, TypeScript, React, Styled Components',
    'Q: What ports does the application use? A: Frontend runs on port 3000, Backend on port 8080',
    'Q: How to setup the project? A: Install Node.js 18+, Python 3.10+, run npm install in frontend, poetry install in backend',
    'Q: What is the database schema? A: Main tables are knowledge_items, user_favorites, and activity_log',
    'Q: What features are available? A: Knowledge management, search & filtering, export, authentication, dashboard',
    'Q: Is the project production ready? A: Yes, version 1.0.0 is fully functional and production ready',
    'Q: What export formats are supported? A: CSV and PDF export via backend API',
    'Q: How is authentication handled? A: Supabase Auth with signup/signin and session management'
  ],
  
  -- Metadata
  'Agent Thread - Knowledge Base Extraction Task',
  '2025-10-27',
  'Ignite Knowledge',
  
  -- Raw Text
  'Full-Stack Knowledge Management Application

FRONTEND STACK:
- Next.js 14.2.5 with TypeScript
- React with hooks (useState, useEffect)
- Styled Components for CSS-in-JS
- Supabase Client for data access
- Responsive design across all devices

BACKEND STACK:
- FastAPI with Python 3.10+
- Poetry for dependency management
- Uvicorn ASGI server
- WeasyPrint for PDF generation
- CORS middleware enabled

DATABASE:
- Supabase PostgreSQL database
- Tables: knowledge_items, user_favorites, activity_log
- UUID primary keys
- Row-Level Security policies
- Real-time subscriptions

KEY FEATURES:
- Knowledge article creation and management
- Full-text search and filtering
- Multi-select project and topic filters
- CSV/PDF export functionality
- User authentication and authorization
- Real-time statistics dashboard
- Summary cards with article, project, and topic counts
- Responsive card-based layout
- User profile management

ARCHITECTURE:
- Frontend (Port 3000): Next.js App Router
- Backend (Port 8080): FastAPI REST API
- Database: Supabase cloud PostgreSQL
- Authentication: Supabase Auth with RLS

DEVELOPMENT:
- Frontend: npm install && npm run dev
- Backend: poetry install && poetry run python app/main.py
- Environment variables configured in .env.local

STATUS: Production Ready (v1.0.0)
Last Updated: October 27, 2025'
);

-- Query to verify the insertion
-- SELECT * FROM public.knowledge_items WHERE project = 'Ignite Knowledge' ORDER BY created_at DESC LIMIT 1;

