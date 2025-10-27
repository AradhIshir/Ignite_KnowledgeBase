# Ignite Knowledge - Project Knowledge Base

## 📋 Quick Reference

**Project Name:** Ignite Knowledge  
**Type:** Team Knowledge Management Application  
**Status:** Production Ready (v1.0.0)  
**Last Updated:** October 27, 2025

---

## 🔑 Main Keywords & Technologies

### **Frontend Technologies**
- **Next.js** 14.2.5 - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **React** - UI component library with hooks (useState, useEffect)
- **Styled Components** - CSS-in-JS styling solution
- **Responsive Design** - Mobile-first approach

### **Backend Technologies**
- **FastAPI** - Modern Python web framework
- **Python** 3.10+ - Core programming language
- **Poetry** - Dependency management
- **Uvicorn** - ASGI server
- **WeasyPrint** - PDF generation
- **CORS** - Cross-origin resource sharing enabled

### **Database & Authentication**
- **Supabase** - Backend-as-a-Service platform
- **PostgreSQL** - Relational database
- **Supabase Auth** - Authentication system
- **Row-Level Security (RLS)** - Database security policies
- **Real-time Subscriptions** - Live data updates

### **Architecture Patterns**
- **Full-Stack Application** - Integrated frontend and backend
- **RESTful API** - Standard API design
- **Component-Based Architecture** - Modular React components
- **Microservices Pattern** - Separated frontend/backend services
- **Client-Server Architecture** - Clear separation of concerns

---

## 🎯 Core Features

### **Knowledge Management**
- Article creation and editing
- Rich metadata support (topics, decisions, FAQs)
- Project categorization
- Source tracking
- Date tracking
- Raw text storage

### **Search & Discovery**
- **Full-text search** across article content
- **Real-time filtering** by project and topics
- **Multi-select filters** for advanced queries
- **Search bar** with instant results

### **Dashboard & Analytics**
- **Summary cards** with real-time statistics
- Total articles count
- Projects overview
- Topics tracking
- **Card-based layout** for content display
- Interactive hover effects

### **Data Management**
- **CSV export** functionality
- **PDF export** capability (via backend)
- Bulk data operations
- Favorites system (planned)
- Activity logging

### **User Experience**
- Clean, modern UI design
- KnowledgeHub-style aesthetic
- Professional header with logo
- User profile management
- Smooth transitions and animations
- Responsive across all devices

---

## 🏗️ System Architecture

### **Project Structure**
```
Ignite Knowledge
├── Frontend (Port 3000)
│   ├── Next.js application
│   ├── TypeScript components
│   └── Styled Components theme
├── Backend (Port 8080)
│   ├── FastAPI server
│   ├── Export services
│   └── Health endpoints
└── Database (Supabase)
    ├── knowledge_items table
    ├── user_favorites table
    └── activity_log table
```

### **Database Schema**

**knowledge_items**
- id (uuid, primary key)
- summary (text)
- topics (text[])
- decisions (text[])
- faqs (text[])
- source (text)
- date (text)
- project (text)
- raw_text (text)
- created_by (uuid, foreign key)
- created_at (timestamp)
- updated_at (timestamp)

**user_favorites**
- user_id (uuid, foreign key)
- item_id (uuid, foreign key)
- created_at (timestamp)

**activity_log**
- id (bigserial)
- user_id (uuid, foreign key)
- action (text)
- item_id (uuid, foreign key)
- created_at (timestamp)

---

## 🎨 Design System

### **Color Palette**
- **Primary Blue:** #1D74F5 (actions, links)
- **Success Green:** #22C7A9 (positive states)
- **Accent Pink:** #EC4899 (highlights)
- **Neutral Grays:** Various shades for text and backgrounds

### **Typography**
- Clean, modern font stack
- Hierarchical heading system
- Readable body text

### **UI Components**
- Navigation bar with logo
- Summary cards with distinct colors
- Knowledge item cards
- Form inputs and buttons
- Modal dialogs
- Filter dropdowns

---

## 🔐 Security Features

### **Authentication**
- Supabase Auth integration
- Sign up / Sign in pages
- Password reset functionality
- Session management
- User profile management

### **Authorization**
- Row-level security policies
- User-specific data access
- Role-based access (admin support)
- Created_by tracking

---

## 📡 API Endpoints

### **Backend API (Port 8080)**
- `GET /health` - Health check endpoint
- `POST /export` - Export data (CSV/PDF)
  - Parameters: filename, format, items[]
- `GET /docs` - FastAPI auto-generated documentation

### **Frontend Routes**
- `/` - Landing page
- `/auth/signup` - User registration
- `/auth/signin` - User login
- `/auth/forgot` - Password reset
- `/app/dashboard` - Main dashboard
- `/app/items` - Articles listing
- `/app/items/new` - Create new article
- `/app/items/[id]` - Article details
- `/app/profile` - User profile
- `/app/admin` - Admin panel

---

## 🚀 Development Workflow

### **Setup Requirements**
- Node.js 18+
- Python 3.10+
- Poetry package manager
- npm or pnpm
- Supabase account

### **Environment Variables**
```
NEXT_PUBLIC_SUPABASE_URL=https://wwmqodqqqrffxdvgisrd.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[key]
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

### **Development Commands**

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
poetry install
poetry run python app/main.py
```

---

## 🎯 Use Cases

### **Primary Use Cases**
1. **Team Knowledge Sharing** - Centralized knowledge repository
2. **Meeting Notes Management** - Store and search meeting outcomes
3. **Decision Tracking** - Record and retrieve important decisions
4. **FAQ Management** - Organize frequently asked questions
5. **Project Documentation** - Project-based knowledge organization

### **User Roles**
- **Regular Users** - Create and view knowledge articles
- **Admins** - Manage users and system configuration
- **Guests** - Limited read-only access (if configured)

---

## 📊 Key Metrics & Features

### **Implemented Features** ✅
- Authentication system
- Modern dashboard
- Knowledge management (CRUD)
- Search and filtering
- Data export (CSV)
- Responsive design
- Professional UI/UX
- Real-time statistics

### **Planned Enhancements** 🔮
- AI assistant integration
- User bookmark/favorites system
- Recent activity tracking
- Advanced full-text search
- Team collaboration features
- Usage analytics and insights
- Performance optimizations
- Comprehensive testing suite
- Production deployment
- Error tracking and monitoring

---

## 🔧 Technical Integrations

### **Third-Party Services**
- **Supabase** - Database, Auth, Real-time
- **Vercel** (potential) - Frontend hosting
- **Render/Railway** (potential) - Backend hosting

### **Development Tools**
- **Poetry** - Python dependency management
- **npm/pnpm** - JavaScript package management
- **Git** - Version control
- **VS Code/Cursor** - IDE

---

## 📝 Code Conventions

### **Frontend**
- TypeScript for type safety
- Functional components with hooks
- Styled Components for styling
- Async/await for API calls
- Error boundary handling

### **Backend**
- FastAPI async endpoints
- Type hints for function signatures
- Poetry for dependencies
- CORS middleware configured
- Health check endpoint

### **Database**
- UUID primary keys
- Timestamps for audit trail
- Foreign key constraints
- RLS policies enabled
- Soft deletes (SET NULL)

---

## 🎓 Learning Resources

### **Key Concepts**
- **Full-Stack Development** - Frontend + Backend + Database
- **Modern React Patterns** - Hooks, Context, Component composition
- **FastAPI Best Practices** - Async, Dependency injection
- **Supabase Integration** - Auth, Database, Real-time
- **TypeScript** - Type safety and interfaces
- **Responsive Design** - Mobile-first approach

### **Project-Specific Knowledge**
- Knowledge management systems
- Search and filtering algorithms
- Data export functionality
- User authentication flows
- Dashboard design patterns

---

## 🐛 Troubleshooting

### **Resolved Issues**
1. Missing `@hookform/resolvers` package - Fixed via npm install
2. Database connection errors - Resolved with new Supabase project
3. Authentication issues - Fixed with proper environment variables
4. Build errors - Resolved dependencies

### **Known Warnings**
- Styled Components `bgColor` prop warning (cosmetic)
- React unknown prop warnings (cosmetic)

---

## 📌 Important Notes

- **Production Ready**: Application is fully functional
- **Database**: Uses Supabase project at wwmqodqqqrffxdvgisrd.supabase.co
- **Port Configuration**: Frontend (3000), Backend (8080)
- **Version**: 1.0.0 as of October 2025
- **Git Branch**: Currently on `cursor/extract-keywords-and-update-knowledge-base-f681`

---

## 🔗 Quick Links

- **GitHub Repository**: /workspace
- **Main README**: /workspace/README.md
- **Frontend README**: /workspace/frontend/README.md
- **Backend README**: /workspace/backend/README.md
- **Database Schema**: /workspace/supabase/schema.sql

---

*This knowledge base is automatically maintained and updated as the project evolves.*
