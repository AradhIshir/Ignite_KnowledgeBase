# Manual Email Confirmation Guide

If you can't access the confirmation link in the email, you can manually confirm the user via Supabase Dashboard.

## Steps:

1. **Go to Supabase Dashboard:**
   - Visit: https://supabase.com/dashboard
   - Select your project: `wwmqodqqqrffxdvgisrd`

2. **Navigate to Authentication:**
   - Click on **"Authentication"** in the left sidebar
   - Click on **"Users"** tab

3. **Find Your User:**
   - Search for: `aradh5@yopmail.com`
   - Click on the user

4. **Manually Confirm Email:**
   - Look for **"Email Confirmed"** toggle or button
   - Enable it or click **"Confirm Email"**
   - The user will now be able to sign in

## Alternative: SQL Query

You can also run this SQL in Supabase SQL Editor:

```sql
UPDATE auth.users 
SET email_confirmed_at = now() 
WHERE email = 'aradh5@yopmail.com';
```

This will manually confirm the email without needing the confirmation link.

