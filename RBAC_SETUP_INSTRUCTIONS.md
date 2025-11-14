# Role-Based Access Control (RBAC) Setup Instructions

## 📋 Overview

This document explains how to set up the 3-role system:
- **Admin**: Can add/delete users, add/delete articles
- **Project Lead**: Can add articles, add comments
- **Team Member**: Read-only access

---

## 🗄️ Step 1: Database Setup

### Run the SQL Schema

1. Go to your **Supabase Dashboard** → **SQL Editor**
2. Copy and paste the contents of `supabase/rbac_schema.sql`
3. Click **Run** to execute

This will create:
- `article_comments` table
- Updated RLS policies for role-based access
- Helper functions

---

## 👥 Step 2: Set User Roles

### Option A: Via Supabase Dashboard (Recommended)

1. Go to **Supabase Dashboard** → **Authentication** → **Users**
2. Click on a user
3. Scroll to **User Metadata**
4. Click **Edit** and add:
   ```json
   {
     "role": "admin"
   }
   ```
   Or `"project_lead"` or `"team_member"`
5. Click **Save**

### Option B: Via Admin Panel (After Setup)

Once the admin panel is set up, you can:
1. Go to `/app/admin` → **Users** tab
2. Create new users with roles
3. Change existing user roles

---

## ⚠️ Important: Supabase Admin API

**The user management features require Supabase Admin API access.**

### Current Limitation:
The frontend code uses `supabase.auth.admin.*` methods which require the **Service Role Key** (not the anon key). For security, this should be done via a backend API.

### Two Options:

#### Option 1: Use Backend API (Recommended)
Create a backend endpoint that uses the Service Role Key:
```python
# backend/app/main.py
from supabase import create_client, Client

SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

@app.post("/api/admin/users")
async def create_user(user_data: dict):
    # Use supabase_admin.auth.admin.create_user()
    pass
```

#### Option 2: Use Supabase Dashboard
For now, manage users directly in Supabase Dashboard until backend is set up.

---

## 🎯 Step 3: Test Roles

### Test Admin:
1. Set a user's role to `"admin"` in Supabase
2. Log in as that user
3. You should see:
   - ✅ "Add Article" button
   - ✅ "Admin" menu item
   - ✅ Can delete articles
   - ✅ Can manage users

### Test Project Lead:
1. Set a user's role to `"project_lead"`
2. Log in as that user
3. You should see:
   - ✅ "Add Article" button
   - ✅ Can add comments on articles
   - ❌ No "Admin" menu
   - ❌ Cannot delete articles

### Test Team Member:
1. Set a user's role to `"team_member"`
2. Log in as that user
3. You should see:
   - ✅ Can view all articles
   - ❌ No "Add Article" button
   - ❌ Cannot add comments
   - ❌ Cannot access admin

---

## 📝 Step 4: Assign Initial Admin

1. Go to **Supabase Dashboard** → **Authentication** → **Users**
2. Find your user account
3. Edit **User Metadata** → Add:
   ```json
   {
     "role": "admin",
     "full_name": "Your Name"
   }
   ```
4. Save and refresh the app

---

## 🔧 Files Created/Modified

### New Files:
- `frontend/src/lib/roles.ts` - Role utility functions
- `frontend/src/components/Comments.tsx` - Comments component
- `supabase/rbac_schema.sql` - Database schema

### Modified Files:
- `frontend/src/pages/app/admin.tsx` - Added Users section
- `frontend/src/pages/app/items/[id].tsx` - Added comments
- `frontend/src/pages/app/items/new.tsx` - Added role checks
- `frontend/src/components/MainMenu.tsx` - Role-based menu

---

## ✅ Verification Checklist

- [ ] Database schema executed successfully
- [ ] At least one user has `admin` role
- [ ] Admin can access `/app/admin` page
- [ ] Admin sees "Users" tab in admin panel
- [ ] Project Lead can create articles
- [ ] Project Lead can add comments
- [ ] Team Member cannot create articles
- [ ] Team Member cannot add comments
- [ ] Navigation shows/hides items based on role

---

## 🚨 Troubleshooting

### "Admins only" message on admin page
- Check user metadata has `role: "admin"`
- Refresh the page after updating role

### Cannot create users in admin panel
- This requires Supabase Service Role Key
- Use Supabase Dashboard for now, or set up backend API

### Comments not showing
- Check `article_comments` table exists
- Verify RLS policies are applied
- Check browser console for errors

### Role not updating
- Clear browser cache
- Sign out and sign back in
- Check Supabase user metadata is saved correctly

---

## 📞 Next Steps

1. **Set up backend API** for user management (recommended)
2. **Test all role permissions**
3. **Assign roles to your team members**
4. **Document your role assignment process**


