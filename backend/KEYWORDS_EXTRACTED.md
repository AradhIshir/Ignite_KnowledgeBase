# Extracted Keywords from Thread Analysis

**Date:** 2025-10-27  
**Source:** Backend/Frontend README files and project documentation  
**Project:** Ignite Knowledge

## Summary

Knowledge base keyword extraction and documentation update - analyzing READMEs for technical keywords and project features

---

## 📋 Topics Identified (20)

1. **Keyword Extraction**
2. **Knowledge Base Management**
3. **Technical Documentation**
4. **FastAPI Backend**
5. **Next.js Frontend**
6. **Supabase Database**
7. **Authentication**
8. **Export Functionality**
9. **React Components**
10. **Styled Components**
11. **TypeScript**
12. **Python**
13. **Poetry**
14. **WeasyPrint**
15. **PDF Generation**
16. **CSV Export**
17. **RESTful API**
18. **Row Level Security**
19. **Theme Management**
20. **User Management**

---

## ✅ Key Decisions (6)

1. Use Supabase for authentication and database management
2. Implement export functionality with CSV and PDF formats
3. Use FastAPI for backend API with ReportLab for PDF generation
4. Use Next.js with TypeScript for frontend development
5. Use Styled Components for theming with blue/green color scheme
6. Implement Row Level Security (RLS) policies for data protection

---

## ❓ FAQs (8)

1. **Q: What backend framework is used?**  
   A: FastAPI with Python 3.10+

2. **Q: What frontend framework is used?**  
   A: Next.js 14.2.5 with TypeScript

3. **Q: How is authentication handled?**  
   A: Supabase Auth with RLS policies

4. **Q: What export formats are supported?**  
   A: CSV and PDF formats

5. **Q: What styling solution is used?**  
   A: Styled Components with custom theme

6. **Q: What database is used?**  
   A: PostgreSQL via Supabase

7. **Q: What package manager is used for Python?**  
   A: Poetry

8. **Q: What port does the backend run on?**  
   A: Port 8080

---

## 🔧 Technical Stack Details

### Backend (FastAPI)
- FastAPI framework
- Python 3.10+ with Poetry
- Export endpoints (CSV/PDF)
- WeasyPrint for PDF generation
- ReportLab for PDF rendering
- CORS middleware
- Uvicorn server
- Port 8080
- Health check endpoint

### Frontend (Next.js)
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

### Database (Supabase)
- PostgreSQL database
- UUID extensions
- `knowledge_items` table (summary, topics, decisions, faqs, source, date, project, raw_text)
- `user_favorites` table
- `activity_log` table
- Row Level Security (RLS)
- Authentication policies
- Triggers for updated_at

### Architecture
- Full-stack application
- RESTful API
- Modern dashboard
- Card-based layout
- Real-time subscriptions
- State management with React hooks
- Profile and session management
- Admin panel
- Export functionality

### Key Features
- Knowledge management system
- Article creation and viewing
- Search with project/topic filters
- CSV/PDF export
- User authentication
- Favorites system
- Activity tracking
- Summary cards with statistics
- Responsive UI/UX

---

## 📝 Next Steps

To insert this data into the knowledge base, run the SQL file in Supabase:

1. Go to your Supabase Dashboard (https://wwmqodqqqrffxdvgisrd.supabase.co)
2. Navigate to SQL Editor
3. Run the SQL file: `backend/insert_keywords.sql`

The SQL file contains all the extracted keywords formatted for insertion into the `knowledge_items` table.

---

## 📁 Generated Files

1. **extract_keywords.py** - Python script for keyword extraction and database insertion
2. **insert_keywords.sql** - SQL script ready to run in Supabase Dashboard
3. **KEYWORDS_EXTRACTED.md** - This summary document

---

*Generated on 2025-10-27*
