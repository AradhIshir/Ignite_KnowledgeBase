# Role-Based Access Control (RBAC) Implementation Plan

## 🎯 Roles Defined

1. **Admin**
   - ✅ Add/Delete users
   - ✅ Add new articles
   - ✅ Delete articles
   - ✅ View all articles
   - ✅ Manage user roles

2. **Project Lead**
   - ✅ Add new articles
   - ✅ Add comments to any article
   - ✅ View all articles
   - ❌ Cannot delete articles
   - ❌ Cannot manage users

3. **Team Member**
   - ✅ View all articles (read-only)
   - ❌ Cannot add articles
   - ❌ Cannot add comments
   - ❌ Cannot delete articles

---

## 📋 Implementation Steps

### Step 1: Database Schema Updates
- [x] Create `comments` table
- [x] Update RLS policies for role-based access
- [x] Create helper function to get user role

### Step 2: User Management UI (Admin)
- [x] Create Users section in admin page
- [x] List all users with their roles
- [x] Add user functionality
- [x] Delete user functionality
- [x] Change user role functionality

### Step 3: Role-Based Access Control
- [x] Create role utility functions
- [x] Update article creation pages (check role)
- [x] Update article deletion (admin only)
- [x] Hide/show UI elements based on role

### Step 4: Comments System
- [x] Create comments component
- [x] Add comments to article detail page
- [x] Only Project Lead and Admin can comment
- [x] Display comments with author and timestamp

### Step 5: Navigation Updates
- [x] Show/hide menu items based on role
- [x] Protect routes with role checks

---

## 🔧 Technical Details

### Role Storage
- Roles stored in Supabase Auth `user_metadata.role`
- Values: `'admin'`, `'project_lead'`, `'team_member'`

### Database Tables Needed
1. `comments` table for article comments
2. Helper function to check user roles

### Frontend Components Needed
1. User Management component (Admin)
2. Comments component (Article detail)
3. Role-based route protection
4. Role utility functions

---

## 📝 Files to Create/Modify

### New Files:
- `frontend/src/lib/roles.ts` - Role utility functions
- `frontend/src/components/Comments.tsx` - Comments component
- `supabase/rbac_schema.sql` - Database schema updates

### Files to Modify:
- `frontend/src/pages/app/admin.tsx` - Add Users section
- `frontend/src/pages/app/items/new.tsx` - Add role check
- `frontend/src/pages/app/items/[id].tsx` - Add comments, role checks
- `frontend/src/pages/app/items/index.tsx` - Hide delete for non-admins
- `frontend/src/components/MainMenu.tsx` - Role-based menu items

---

## ✅ Next Steps

1. Review and approve this plan
2. Implement database schema
3. Create frontend components
4. Add role checks throughout
5. Test all role permissions




