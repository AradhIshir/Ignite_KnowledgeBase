# 🚀 Quick Deploy to Vercel (5 Minutes)

## Step 1: Go to Vercel
Visit: **https://vercel.com** and sign in with GitHub

## Step 2: Import Your Repository
1. Click **"Add New Project"**
2. Select **"Import Git Repository"**
3. Choose: **`AradhIshir/Ignite_KnowledgeBase`**
4. Click **"Import"**

## Step 3: Configure Project Settings
In the project configuration:

- **Framework Preset**: `Next.js` (auto-detected ✅)
- **Root Directory**: Click "Edit" → Set to `frontend`
- **Build Command**: `npm run build` (default)
- **Output Directory**: `.next` (default)
- **Install Command**: `npm install` (default)

## Step 4: Add Environment Variables
Click **"Environment Variables"** and add these:

```
NEXT_PUBLIC_SUPABASE_URL = https://wwmqodqqqrffxdvgisrd.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = [Your Supabase Anon Key]
NEXT_PUBLIC_BACKEND_URL = http://localhost:8080
```

> **Note**: You can update `NEXT_PUBLIC_BACKEND_URL` later if you deploy the backend.

## Step 5: Deploy!
1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Get your public URL: `https://your-app-name.vercel.app` 🎉

## Step 6: Update Supabase Settings
1. Go to **Supabase Dashboard** → **Authentication** → **URL Configuration**
2. Add to **Redirect URLs**:
   - `https://your-app-name.vercel.app/auth/callback`
   - `https://your-app-name.vercel.app/auth/update-password`
3. Set **Site URL**: `https://your-app-name.vercel.app`
4. Click **Save**

## ✅ Done!
Share this URL with your team: `https://your-app-name.vercel.app`

---

## 🔄 Updating Your Deployment
Every time you push to GitHub, Vercel will automatically redeploy your app!

## 📝 Need Help?
- Check deployment logs in Vercel dashboard
- Verify environment variables are set correctly
- Make sure Supabase redirect URLs are updated

