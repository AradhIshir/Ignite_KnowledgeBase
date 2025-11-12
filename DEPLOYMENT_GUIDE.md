# Deployment Guide - Making Your App Public

This guide will help you deploy your Knowledge Base application so your team can access it via a public URL.

## 🚀 Quick Deployment Options

### Option 1: Vercel (Recommended for Frontend)
**Best for:** Next.js frontend deployment
**Free tier:** Yes
**Setup time:** ~5 minutes

### Option 2: Railway (For Full-Stack)
**Best for:** Both frontend and backend
**Free tier:** Yes (with credit card)
**Setup time:** ~10 minutes

---

## 📋 Step-by-Step: Deploy to Vercel (Recommended)

### Prerequisites
- GitHub account (your code is already on GitHub)
- Vercel account (free at vercel.com)

### Step 1: Deploy Frontend to Vercel

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** with your GitHub account
3. **Click "Add New Project"**
4. **Import your repository**: `AradhIshir/Ignite_KnowledgeBase`
5. **Configure the project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

6. **Add Environment Variables**:
   Click "Environment Variables" and add:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://wwmqodqqqrffxdvgisrd.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
   NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.railway.app
   ```
   (Update the backend URL after deploying backend)

7. **Click "Deploy"**
8. **Wait for deployment** (~2-3 minutes)
9. **Get your public URL**: `https://your-app-name.vercel.app`

### Step 2: Deploy Backend to Railway (Optional)

The backend is mainly used for CSV/PDF exports. If you need this feature:

1. **Go to Railway**: https://railway.app
2. **Sign up** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select your repository**
5. **Configure**:
   - **Root Directory**: `backend`
   - **Start Command**: `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
6. **Add Environment Variables**:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - (Any other backend env vars)

7. **Get your backend URL** and update the frontend env var

---

## 🔧 Alternative: Deploy Both to Railway

If you prefer one platform:

1. **Deploy Frontend**:
   - Root: `frontend`
   - Build: `npm install && npm run build`
   - Start: `npm start`
   - Port: 3000

2. **Deploy Backend**:
   - Root: `backend`
   - Build: `poetry install`
   - Start: `poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## ⚙️ Environment Variables Checklist

### Frontend (Vercel/Railway)
```
NEXT_PUBLIC_SUPABASE_URL=https://wwmqodqqqrffxdvgisrd.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.railway.app
```

### Backend (Railway - if deploying)
```
SUPABASE_URL=https://wwmqodqqqrffxdvgisrd.supabase.co
SUPABASE_ANON_KEY=your_anon_key
```

---

## 🔗 Update Supabase Redirect URLs

After deployment, update Supabase auth settings:

1. Go to **Supabase Dashboard** → **Authentication** → **URL Configuration**
2. Add to **Redirect URLs**:
   - `https://your-app.vercel.app/auth/callback`
   - `https://your-app.vercel.app/auth/update-password`
3. Add to **Site URL**: `https://your-app.vercel.app`

---

## 📝 Post-Deployment Checklist

- [ ] Frontend deployed and accessible
- [ ] Environment variables set correctly
- [ ] Supabase redirect URLs updated
- [ ] Test sign up / sign in
- [ ] Test password reset flow
- [ ] Backend deployed (if needed)
- [ ] Share URL with team!

---

## 🆘 Troubleshooting

### Frontend shows "Cannot connect to Supabase"
- Check environment variables are set correctly
- Ensure `NEXT_PUBLIC_` prefix is used
- Redeploy after changing env vars

### Auth redirects not working
- Update Supabase redirect URLs
- Check callback URL matches exactly

### Backend not accessible
- Check Railway deployment logs
- Verify PORT environment variable
- Ensure start command is correct

---

## 🎉 You're Done!

Once deployed, share your public URL with your team:
- **Frontend**: `https://your-app.vercel.app`
- **Backend** (if deployed): `https://your-backend.railway.app`

