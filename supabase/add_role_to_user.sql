-- Add role to existing user metadata (preserves existing fields)
-- Replace 'agoyal@ishir.com' with your email
-- Replace 'admin' with the role you want: 'admin', 'project_lead', or 'team_member'

UPDATE auth.users
SET raw_user_meta_data = raw_user_meta_data || '{"role": "admin"}'::jsonb
WHERE email = 'agoyal@ishir.com';

-- Verify the update:
SELECT 
  email,
  raw_user_meta_data->>'role' as role,
  raw_user_meta_data->>'full_name' as full_name,
  raw_user_meta_data
FROM auth.users
WHERE email = 'agoyal@ishir.com';




