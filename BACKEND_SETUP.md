# Backend Setup for User Management

## 🔧 Required Environment Variables

The backend needs these environment variables to enable user management:

### 1. Get Your Supabase Keys

1. Go to **Supabase Dashboard** → **Project Settings** → **API**
2. Copy these values:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_SERVICE_ROLE_KEY` ⚠️ **Keep this secret!**

### 2. Set Environment Variables

#### Option A: Create `.env` file in `backend/` folder

```bash
cd backend
touch .env
```

Add to `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
PORT=8080
```

#### Option B: Export in terminal (temporary)

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key-here"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key-here"
export PORT=8080
```

---

## 🚀 Start the Backend

```bash
cd backend
poetry install  # If not already done
poetry run uvicorn app.main:app --reload --port 8080
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
```

---

## ✅ Verify It's Working

1. **Check health endpoint:**
   ```bash
   curl http://localhost:8080/health
   ```
   Should return: `{"ok": true}`

2. **Check API docs:**
   Open http://localhost:8080/docs in your browser
   You should see the new endpoints:
   - `GET /api/admin/users` - List users
   - `POST /api/admin/users` - Create user
   - `DELETE /api/admin/users/{user_id}` - Delete user
   - `PATCH /api/admin/users/{user_id}/role` - Update role

---

## 🔒 Security Notes

- ⚠️ **NEVER** commit `.env` file to git
- ⚠️ **NEVER** expose `SUPABASE_SERVICE_ROLE_KEY` in frontend code
- ✅ The backend uses this key securely on the server side
- ✅ Frontend sends auth token, backend verifies admin role

---

## 🐛 Troubleshooting

### "Supabase admin client not configured"
- Check that `SUPABASE_SERVICE_ROLE_KEY` is set
- Restart the backend after setting environment variables

### "Admin access required" error
- Make sure your user has `role: "admin"` in user metadata
- Log out and log back in after updating role

### "Failed to fetch users"
- Check backend is running on port 8080
- Check `NEXT_PUBLIC_BACKEND_URL` in frontend `.env` is set to `http://localhost:8080`
- Check browser console for CORS errors

---

## 📝 Frontend Configuration

Make sure your frontend `.env.local` has:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8080
```

---

## 🎯 Next Steps

1. ✅ Set environment variables
2. ✅ Start backend server
3. ✅ Verify endpoints work
4. ✅ Test user management in admin panel

