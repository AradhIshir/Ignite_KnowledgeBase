-- Migration: Add columns for AI-generated summaries
-- This adds key_points and action_items columns to store structured AI summary data
-- Run this in your Supabase SQL Editor

-- Add key_points column (array of text)
ALTER TABLE public.knowledge_items 
ADD COLUMN IF NOT EXISTS key_points text[] NULL;

-- Add action_items column (array of text) - separate from faqs
ALTER TABLE public.knowledge_items 
ADD COLUMN IF NOT EXISTS action_items text[] NULL;

-- Add comment to document the columns
COMMENT ON COLUMN public.knowledge_items.key_points IS 'Key points extracted from AI analysis of conversation threads';
COMMENT ON COLUMN public.knowledge_items.action_items IS 'Action items extracted from AI analysis of conversation threads';

-- Verify the columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'knowledge_items'
  AND column_name IN ('key_points', 'action_items');


