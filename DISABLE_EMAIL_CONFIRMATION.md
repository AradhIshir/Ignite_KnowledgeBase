# Disable Email Confirmation in Supabase

This guide will help you disable email confirmation so users can sign in immediately after creating an account.

## Steps to Disable Email Confirmation

### 1. Go to Supabase Dashboard
- Visit: https://supabase.com/dashboard
- Select your project: `wwmqodqqqrffxdvgisrd`

### 2. Navigate to Authentication Settings
- Click on **"Authentication"** in the left sidebar
- Click on **"Settings"** (or "Configuration")

### 3. Disable Email Confirmation
- Find the section **"Email Auth"** or **"Email Settings"**
- Look for **"Enable email confirmations"** toggle
- **Turn it OFF** (disable it)
- Click **"Save"** or **"Update"**

### 4. Verify the Change
- The setting should now show as disabled
- New users can now sign in immediately after signup
- Users will still receive a welcome email (notification only, no confirmation required)

## What This Changes

✅ **Before:** Users must click a confirmation link in email before signing in  
✅ **After:** Users can sign in immediately after creating an account  
✅ **Email:** Users still receive a welcome/notification email (but no confirmation needed)

## Testing

1. Create a new account at: http://localhost:3000/auth/signup
2. You should be automatically redirected to the dashboard
3. No email confirmation required!

## Note

- Existing unconfirmed users will still need to be manually confirmed or can sign up again
- You can manually confirm existing users in Supabase Dashboard → Authentication → Users

