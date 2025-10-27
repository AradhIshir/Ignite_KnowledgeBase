-- Complete schema for new Supabase project
-- Run this in a fresh Supabase project

-- Enable UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Knowledge items table
CREATE TABLE IF NOT EXISTS public.knowledge_items (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  summary text NOT NULL,
  topics text[] NULL,
  decisions text[] NULL,
  faqs text[] NULL,
  source text NULL,
  date text NULL,
  project text NULL,
  raw_text text NULL,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- User favorites table
CREATE TABLE IF NOT EXISTS public.user_favorites (
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  item_id uuid REFERENCES public.knowledge_items(id) ON DELETE CASCADE,
  created_at timestamp with time zone DEFAULT now(),
  PRIMARY KEY (user_id, item_id)
);

-- Activity log table
CREATE TABLE IF NOT EXISTS public.activity_log (
  id bigserial PRIMARY KEY,
  user_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  action text NOT NULL,
  item_id uuid REFERENCES public.knowledge_items(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.knowledge_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_log ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY ki_select ON public.knowledge_items FOR SELECT USING (true);
CREATE POLICY ki_insert ON public.knowledge_items FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY ki_update ON public.knowledge_items FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY ki_delete ON public.knowledge_items FOR DELETE USING (auth.role() = 'authenticated');

CREATE POLICY fav_select ON public.user_favorites FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY fav_insert ON public.user_favorites FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY fav_delete ON public.user_favorites FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY act_select ON public.activity_log FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY act_insert ON public.activity_log FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at 
  BEFORE UPDATE ON public.knowledge_items
  FOR EACH ROW 
  EXECUTE FUNCTION public.set_updated_at();


