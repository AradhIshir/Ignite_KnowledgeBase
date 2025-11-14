-- Update User Role via SQL
-- Replace 'agoyal@ishir.com' with your email
-- Replace 'admin' with the role you want: 'admin', 'project_lead', or 'team_member'

UPDATE auth.users
SET raw_user_meta_data = jsonb_set(
  COALESCE(raw_user_meta_data, '{}'::jsonb),
  '{role}',
  '"admin"'::jsonb
)
WHERE email = 'agoyal@ishir.com';

-- To also add full_name:
UPDATE auth.users
SET raw_user_meta_data = jsonb_set(
  COALESCE(raw_user_meta_data, '{}'::jsonb),
  '{full_name}',
  '"Aradhana Goyal"'::jsonb
)
WHERE email = 'agoyal@ishir.com';

-- Or combine both in one update:
UPDATE auth.users
SET raw_user_meta_data = jsonb_build_object(
  'role', 'admin',
  'full_name', 'Aradhana Goyal'
)
WHERE email = 'agoyal@ishir.com';

-- Verify the update:
SELECT 
  email,
  raw_user_meta_data->>'role' as role,
  raw_user_meta_data->>'full_name' as full_name
FROM auth.users
WHERE email = 'agoyal@ishir.com';


