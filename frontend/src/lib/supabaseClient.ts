import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string;

if (!supabaseUrl || !supabaseAnonKey) {
  // Fail fast so env is clearly required in dev
  throw new Error('Missing Supabase environment variables. Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
});

export type Database = {
  public: {
    Tables: {
      knowledge_items: {
        Row: {
          id: string;
          summary: string;
          topics: string[] | null;
          decisions: string[] | null;
          faqs: string[] | null;
          source: string | null;
          date: string | null;
          project: string | null;
          raw_text: string | null;
          created_at: string;
          updated_at: string;
          created_by: string | null;
        };
        Insert: Partial<Omit<Database['public']['Tables']['knowledge_items']['Row'], 'id' | 'created_at' | 'updated_at'>> & {
          summary: string;
        };
        Update: Partial<Database['public']['Tables']['knowledge_items']['Row']>;
      };
    };
  };
};

