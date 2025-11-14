# Extracted Keywords - Ignite Knowledge Project

**Date:** 2025-10-27  
**Source:** Agent Thread - Knowledge Base Extraction Task  
**Project:** Ignite Knowledge

---

## Summary

Project Keywords and Technical Stack Documentation - Extracted main keywords from Ignite Knowledge project covering full-stack architecture, technologies, features, and development workflow

---

## Topics (Keywords)

### Frontend Technologies
- Next.js
- TypeScript
- React
- Styled Components
- Responsive Design

### Backend Technologies
- FastAPI
- Python
- Poetry
- CSV Export
- PDF Export

### Database & Infrastructure
- Supabase
- PostgreSQL
- Row-Level Security
- Real-time Subscriptions
- Authentication

### Features & Capabilities
- Knowledge Management
- Search & Filtering
- Dashboard
- Full-Stack Development
- RESTful API

---

## Key Decisions

1. **Use Next.js 14.2.5 for frontend framework** - Modern React framework with App Router for better performance and developer experience

2. **Implement FastAPI for backend services** - High-performance Python framework with automatic API documentation

3. **Choose Supabase for database and authentication** - Complete backend solution with PostgreSQL, Auth, and real-time capabilities

4. **Use Styled Components for styling solution** - CSS-in-JS for component-scoped styling and theming

5. **Implement Poetry for Python dependency management** - Modern Python package manager with better dependency resolution

6. **Enable CORS for cross-origin requests** - Allow frontend-backend communication across different ports

7. **Use Row-Level Security policies for data protection** - Database-level security for multi-tenant data access

8. **Implement real-time subscriptions for live updates** - Real-time data synchronization using Supabase subscriptions

9. **Create modular component-based architecture** - Reusable React components for maintainability

10. **Support CSV and PDF export formats** - Multiple export options for knowledge items

---

## Frequently Asked Questions (FAQs)

### Q: What technologies are used?
**A:** Next.js, FastAPI, Supabase, TypeScript, React, Styled Components

### Q: What ports does the application use?
**A:** Frontend runs on port 3000, Backend on port 8080

### Q: How to setup the project?
**A:** Install Node.js 18+, Python 3.10+, run npm install in frontend, poetry install in backend

### Q: What is the database schema?
**A:** Main tables are knowledge_items, user_favorites, and activity_log

### Q: What features are available?
**A:** Knowledge management, search & filtering, export, authentication, dashboard

### Q: Is the project production ready?
**A:** Yes, version 1.0.0 is fully functional and production ready

### Q: What export formats are supported?
**A:** CSV and PDF export via backend API

### Q: How is authentication handled?
**A:** Supabase Auth with signup/signin and session management

---

## Full Technical Context

### Frontend Stack
- Next.js 14.2.5 with TypeScript
- React with hooks (useState, useEffect)
- Styled Components for CSS-in-JS
- Supabase Client for data access
- Responsive design across all devices

### Backend Stack
- FastAPI with Python 3.10+
- Poetry for dependency management
- Uvicorn ASGI server
- WeasyPrint for PDF generation
- CORS middleware enabled

### Database
- Supabase PostgreSQL database
- Tables: knowledge_items, user_favorites, activity_log
- UUID primary keys
- Row-Level Security policies
- Real-time subscriptions

### Key Features
- Knowledge article creation and management
- Full-text search and filtering
- Multi-select project and topic filters
- CSV/PDF export functionality
- User authentication and authorization
- Real-time statistics dashboard
- Summary cards with article, project, and topic counts
- Responsive card-based layout
- User profile management

### Architecture
- Frontend (Port 3000): Next.js App Router
- Backend (Port 8080): FastAPI REST API
- Database: Supabase cloud PostgreSQL
- Authentication: Supabase Auth with RLS

### Development
- Frontend: npm install && npm run dev
- Backend: poetry install && poetry run python app/main.py
- Environment variables configured in .env.local

**Status:** Production Ready (v1.0.0)  
**Last Updated:** October 27, 2025

