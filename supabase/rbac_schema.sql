-- Role-Based Access Control (RBAC) Schema Updates
-- Run this in your Supabase SQL Editor

-- ============================================================================
-- 1. Create Comments Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.article_comments (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  article_id uuid NOT NULL REFERENCES public.knowledge_items(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  comment_text text NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Enable RLS on comments
ALTER TABLE public.article_comments ENABLE ROW LEVEL SECURITY;

-- Comments policies:
-- - Everyone can read comments
-- - Only authenticated users with project_lead or admin role can insert
-- - Users can update/delete their own comments
DROP POLICY IF EXISTS comments_select ON public.article_comments;
CREATE POLICY comments_select ON public.article_comments
  FOR SELECT USING (true);

DROP POLICY IF EXISTS comments_insert ON public.article_comments;
CREATE POLICY comments_insert ON public.article_comments
  FOR INSERT 
  WITH CHECK (
    auth.role() = 'authenticated' AND
    (
      (auth.jwt() -> 'user_metadata' ->> 'role')::text IN ('admin', 'project_lead')
    )
  );

DROP POLICY IF EXISTS comments_update ON public.article_comments;
CREATE POLICY comments_update ON public.article_comments
  FOR UPDATE 
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS comments_delete ON public.article_comments;
CREATE POLICY comments_delete ON public.article_comments
  FOR DELETE 
  USING (auth.uid() = user_id OR (auth.jwt() -> 'user_metadata' ->> 'role')::text = 'admin');

-- Trigger for updated_at
CREATE TRIGGER set_updated_at_comments
  BEFORE UPDATE ON public.article_comments
  FOR EACH ROW
  EXECUTE FUNCTION public.set_updated_at();

-- ============================================================================
-- 2. Update Knowledge Items RLS Policies (Role-Based)
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS ki_select ON public.knowledge_items;
DROP POLICY IF EXISTS ki_insert ON public.knowledge_items;
DROP POLICY IF EXISTS ki_update ON public.knowledge_items;
DROP POLICY IF EXISTS ki_delete ON public.knowledge_items;

-- New role-based policies:
-- SELECT: Everyone can read (team_member, project_lead, admin)
CREATE POLICY ki_select ON public.knowledge_items
  FOR SELECT USING (true);

-- INSERT: Admin and Project Lead can create articles
DROP POLICY IF EXISTS ki_insert ON public.knowledge_items;
CREATE POLICY ki_insert ON public.knowledge_items
  FOR INSERT 
  WITH CHECK (
    auth.role() = 'authenticated' AND
    (
      (auth.jwt() -> 'user_metadata' ->> 'role')::text IN ('admin', 'project_lead')
    )
  );

-- UPDATE: Admin and Project Lead can update (or creator)
DROP POLICY IF EXISTS ki_update ON public.knowledge_items;
CREATE POLICY ki_update ON public.knowledge_items
  FOR UPDATE 
  USING (
    auth.role() = 'authenticated' AND
    (
      (auth.jwt() -> 'user_metadata' ->> 'role')::text IN ('admin', 'project_lead') OR
      created_by = auth.uid()
    )
  );

-- DELETE: Only Admin can delete articles
DROP POLICY IF EXISTS ki_delete ON public.knowledge_items;
CREATE POLICY ki_delete ON public.knowledge_items
  FOR DELETE 
  USING (
    auth.role() = 'authenticated' AND
    (auth.jwt() -> 'user_metadata' ->> 'role')::text = 'admin'
  );

-- ============================================================================
-- 3. Helper Function to Get User Role
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_user_role(user_id uuid)
RETURNS text AS $$
BEGIN
  RETURN (
    SELECT (raw_user_meta_data->>'role')::text
    FROM auth.users
    WHERE id = user_id
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 4. Create Indexes for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_comments_article_id ON public.article_comments(article_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON public.article_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON public.article_comments(created_at DESC);

-- ============================================================================
-- 5. Grant Permissions
-- ============================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON public.article_comments TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_user_role TO authenticated;

