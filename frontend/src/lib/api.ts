import { supabase } from './supabaseClient';

// ============================================================================
// Auth API
// ============================================================================

export async function signUp(userData: {
  email: string;
  password: string;
  full_name: string;
}) {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backend) {
    throw new Error('Backend URL is not configured. Please check your environment variables.');
  }
  
  try {
    const res = await fetch(`${backend}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || `Failed to create account (${res.status})`);
    }
    
    return await res.json();
  } catch (err: any) {
    if (err.message.includes('Backend URL')) {
      throw err;
    }
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8080.');
    }
    throw err;
  }
}

// ============================================================================
// Knowledge Items API
// ============================================================================

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
  try {
    const { data, error } = await supabase.from('knowledge_items').upsert(payload).select().maybeSingle();
    if (error) {
      // Provide more user-friendly error messages
      if (error.code === 'PGRST116') {
        throw new Error('You do not have permission to create articles. Please check your role.');
      } else if (error.message.includes('permission') || error.message.includes('policy')) {
        throw new Error('You do not have permission to create articles. Only Admins and Project Leads can create articles.');
      } else if (error.message.includes('authentication')) {
        throw new Error('You must be logged in to create articles. Please log in and try again.');
      } else if (error.message.includes('violates') || error.message.includes('constraint')) {
        throw new Error('Invalid data provided. Please check all required fields.');
      }
      throw new Error(error.message || 'Failed to save article. Please try again.');
    }
    return data;
  } catch (err: any) {
    if (err.message) {
      throw err;
    }
    throw new Error('An unexpected error occurred while saving the article. Please try again.');
  }
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

// ============================================================================
// User Management API (Admin Only)
// ============================================================================

async function getAuthHeaders() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new Error('Not authenticated');
  }
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session.access_token}`,
  };
}

export async function listUsers() {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backend) {
    throw new Error('Backend URL is not configured. Please check your environment variables.');
  }
  
  try {
    const headers = await getAuthHeaders();
    const res = await fetch(`${backend}/api/admin/users`, {
      method: 'GET',
      headers,
    });
    
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      
      if (res.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      } else if (res.status === 403) {
        throw new Error('You do not have permission to view users. Admin access required.');
      } else if (res.status === 500) {
        throw new Error('Server error. Please check if the backend is running and configured correctly.');
      }
      
      throw new Error(error.detail || `Failed to fetch users (${res.status})`);
    }
    
    const data = await res.json();
    return data.users || [];
  } catch (err: any) {
    if (err.message.includes('Backend URL')) {
      throw err;
    }
    if (err.message.includes('Not authenticated')) {
      throw new Error('You must be logged in to view users.');
    }
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8080.');
    }
    throw err;
  }
}

export async function createUser(userData: {
  email: string;
  password: string;
  full_name: string;
  role: 'admin' | 'project_lead' | 'team_member';
}) {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backend) {
    throw new Error('Backend URL is not configured. Please check your environment variables.');
  }
  
  try {
    const headers = await getAuthHeaders();
    const res = await fetch(`${backend}/api/admin/users`, {
      method: 'POST',
      headers,
      body: JSON.stringify(userData),
    });
    
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      
      if (res.status === 400) {
        throw new Error(error.detail || 'Invalid user data. Please check all fields and try again.');
      } else if (res.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      } else if (res.status === 403) {
        throw new Error('You do not have permission to create users. Admin access required.');
      } else if (res.status === 500) {
        throw new Error('Server error. The user may already exist or the backend is not configured correctly.');
      }
      
      throw new Error(error.detail || `Failed to create user (${res.status})`);
    }
    
    return await res.json();
  } catch (err: any) {
    if (err.message.includes('Backend URL')) {
      throw err;
    }
    if (err.message.includes('Not authenticated')) {
      throw new Error('You must be logged in to create users.');
    }
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8080.');
    }
    throw err;
  }
}

export async function deleteUser(userId: string) {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backend) {
    throw new Error('Backend URL is not configured. Please check your environment variables.');
  }
  
  try {
    const headers = await getAuthHeaders();
    const res = await fetch(`${backend}/api/admin/users/${userId}`, {
      method: 'DELETE',
      headers,
    });
    
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      
      if (res.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      } else if (res.status === 403) {
        throw new Error('You do not have permission to delete users. Admin access required.');
      } else if (res.status === 404) {
        throw new Error('User not found. They may have already been deleted.');
      } else if (res.status === 500) {
        throw new Error('Server error. Please try again later.');
      }
      
      throw new Error(error.detail || `Failed to delete user (${res.status})`);
    }
    
    return await res.json();
  } catch (err: any) {
    if (err.message.includes('Backend URL')) {
      throw err;
    }
    if (err.message.includes('Not authenticated')) {
      throw new Error('You must be logged in to delete users.');
    }
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8080.');
    }
    throw err;
  }
}

export async function updateUserRole(userId: string, role: 'admin' | 'project_lead' | 'team_member') {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backend) {
    throw new Error('Backend URL is not configured. Please check your environment variables.');
  }
  
  try {
    const headers = await getAuthHeaders();
    const res = await fetch(`${backend}/api/admin/users/${userId}/role`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ role }),
    });
    
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      
      if (res.status === 400) {
        throw new Error(error.detail || 'Invalid role. Please select a valid role.');
      } else if (res.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      } else if (res.status === 403) {
        throw new Error('You do not have permission to update user roles. Admin access required.');
      } else if (res.status === 404) {
        throw new Error('User not found. They may have been deleted.');
      } else if (res.status === 500) {
        throw new Error('Server error. Please try again later.');
      }
      
      throw new Error(error.detail || `Failed to update user role (${res.status})`);
    }
    
    return await res.json();
  } catch (err: any) {
    if (err.message.includes('Backend URL')) {
      throw err;
    }
    if (err.message.includes('Not authenticated')) {
      throw new Error('You must be logged in to update user roles.');
    }
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Cannot connect to backend server. Please ensure the backend is running on port 8080.');
    }
    throw err;
  }
}

