import { supabase } from './supabaseClient';

export async function listKnowledge(params?: { limit?: number }) {
  const { data, error } = await supabase
    .from('knowledge_items')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(params?.limit ?? 100);
  if (error) throw error;
  return data;
}

export async function getKnowledge(id: string) {
  const { data, error } = await supabase
    .from('knowledge_items')
    .select('*')
    .eq('id', id)
    .maybeSingle();
  if (error) throw error;
  return data;
}

export async function upsertKnowledge(payload: Record<string, unknown>) {
  const { data, error } = await supabase.from('knowledge_items').upsert(payload).select().maybeSingle();
  if (error) throw error;
  return data;
}

export async function removeKnowledge(id: string) {
  const { error } = await supabase.from('knowledge_items').delete().eq('id', id);
  if (error) throw error;
}

export async function toggleFavorite(itemId: string, favorite: boolean) {
  if (favorite) {
    const { error } = await supabase.from('user_favorites').insert({ item_id: itemId, user_id: (await supabase.auth.getUser()).data.user?.id });
    if (error) throw error;
  } else {
    const { error } = await supabase.from('user_favorites').delete().eq('item_id', itemId).eq('user_id', (await supabase.auth.getUser()).data.user?.id ?? '');
    if (error) throw error;
  }
}

export async function listFavorites() {
  const userId = (await supabase.auth.getUser()).data.user?.id;
  if (!userId) return [];
  const { data, error } = await supabase.from('user_favorites').select('item_id');
  if (error) throw error;
  return data?.map((d) => d.item_id) as string[];
}

export async function exportItems(format: 'csv' | 'pdf', items: any[], filename = 'knowledge') {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL;
  const res = await fetch(`${backend}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, format, items })
  });
  if (!res.ok) throw new Error('Failed to export');
  return res.json();
}

