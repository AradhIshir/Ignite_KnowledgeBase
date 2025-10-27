/**
 * Script to extract keywords from the conversation thread and update Supabase knowledge_items table
 * Run with: npx tsx scripts/update-knowledge-base.ts
 */

import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://wwmqodqqqrffxdvgisrd.supabase.co";
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3bXFvZHFxcXJmZnhkdmdpc3JkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEyNzkwODIsImV4cCI6MjA3Njg1NTA4Mn0.Af0VXHqBc-rEHy8jbcXcCakpPFfyE_B_koOAiAS_ZcI";

const supabase = createClient(supabaseUrl, supabaseKey);

// Main keywords extracted from the thread based on the technical stack in READMEs
const TOPICS = [
  "Keyword Extraction",
  "Knowledge Base Management",
  "Supabase Integration",
  "Database Schema",
  "Backend Development",
  "Frontend Development",
  "Python Scripting",
  "Data Analysis",
  "Next.js",
  "FastAPI",
  "TypeScript"
];

// Key technical decisions/components mentioned in the READMEs
const DECISIONS = [
  "Use Next.js for frontend framework",
  "Use FastAPI for backend API",
  "Use Supabase for authentication and database",
  "Use styled-components for UI theming",
  "Implement RLS policies for security",
  "Support CSV and PDF export functionality",
  "Use Poetry for Python dependency management",
  "Implement row-level security for data protection"
];

// FAQs based on the application architecture
const FAQS = [
  "Q: What database is used? A: PostgreSQL via Supabase with knowledge_items, user_favorites, and activity_log tables",
  "Q: What are the main tables? A: knowledge_items (stores articles), user_favorites (bookmarks), activity_log (tracking)",
  "Q: How is authentication handled? A: Supabase Auth with row-level security (RLS) policies",
  "Q: What export formats are supported? A: CSV (built-in) and PDF (via WeasyPrint)",
  "Q: What ports do services run on? A: Frontend on 3000, Backend on 8080",
  "Q: What is the tech stack? A: Next.js + TypeScript frontend, FastAPI + Python backend, Supabase PostgreSQL database",
  "Q: How to extract keywords? A: Analyze README files and conversation context to identify key topics, decisions, and FAQs"
];

async function main() {
  try {
    // Create a test user session or use existing credentials
    // For this script, we'll use the service to insert without auth
    // by temporarily using the anon key with the select policy
    
    const knowledgeItem = {
      summary: "Thread about extracting keywords from conversation and updating Supabase knowledge base. Analyzed the application architecture including Next.js frontend, FastAPI backend, and Supabase database. Identified main technical topics, architectural decisions, and key FAQs from the README documentation.",
      topics: TOPICS,
      decisions: DECISIONS,
      faqs: FAQS,
      source: "Cursor Agent Thread - Keyword Extraction",
      date: new Date().toISOString().split('T')[0],
      project: "Ignite Knowledge - Team Knowledge Base",
      raw_text: `
This thread involved extracting main keywords from a conversation based on the technical stack 
and architecture documented in the project READMEs. The application is a full-stack knowledge 
management system built with:

Frontend: Next.js 14.2.5 with TypeScript, Styled Components, Supabase Auth
Backend: FastAPI with Python 3.10+, Poetry, Export functionality (CSV/PDF)
Database: Supabase PostgreSQL with tables for knowledge_items, user_favorites, and activity_log

The knowledge_items table schema includes fields for summary, topics (text[]), decisions (text[]), 
faqs (text[]), source, date, project, raw_text, and tracking fields (created_by, created_at, updated_at).

Key architectural decisions include using Supabase for auth/database, implementing RLS policies for 
security, and supporting multiple export formats. The application is currently in production-ready 
status with full CRUD functionality, search/filtering, and modern UI/UX.

Keywords extracted: ${TOPICS.join(', ')}

This knowledge item serves as documentation of the keyword extraction process and the technical 
architecture of the Ignite Knowledge application.
      `.trim()
    };

    console.log('📝 Preparing to insert knowledge item...');
    console.log(`📊 Topics: ${TOPICS.length} topics extracted`);
    console.log(`🎯 Decisions: ${DECISIONS.length} key decisions documented`);
    console.log(`❓ FAQs: ${FAQS.length} FAQs created`);
    
    // Note: This requires authentication. The insert will work if:
    // 1. A user is signed in, or
    // 2. The RLS policy is updated to allow inserts, or
    // 3. A service role key is used
    
    const { data, error } = await supabase
      .from('knowledge_items')
      .insert(knowledgeItem)
      .select();

    if (error) {
      console.error('❌ Error inserting knowledge item:', error);
      console.log('\n💡 Tip: This script requires authentication. Options:');
      console.log('   1. Sign in to the app and run this from a logged-in context');
      console.log('   2. Use a service role key instead of anon key');
      console.log('   3. Update RLS policy to allow anonymous inserts (not recommended)');
      console.log('\n📋 Knowledge item prepared (not inserted):');
      console.log(JSON.stringify(knowledgeItem, null, 2));
      process.exit(1);
    }

    console.log('✅ Successfully inserted knowledge item into Supabase!');
    console.log(`📝 Item ID: ${data[0].id}`);
    console.log(`\nSummary: ${knowledgeItem.summary.substring(0, 100)}...`);
    
  } catch (error) {
    console.error('❌ Unexpected error:', error);
    process.exit(1);
  }
}

main();
