/**
 * Role-Based Access Control (RBAC) Utilities
 * 
 * Roles:
 * - 'admin': Full access - can manage users, add/delete articles
 * - 'project_lead': Can add articles and comments
 * - 'team_member': Read-only access
 */

import { supabase } from './supabaseClient';

export type UserRole = 'admin' | 'project_lead' | 'team_member' | null;

/**
 * Get the current user's role
 */
export async function getUserRole(): Promise<UserRole> {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return null;
    
    const role = (user.user_metadata as any)?.role;
    if (['admin', 'project_lead', 'team_member'].includes(role)) {
      return role as UserRole;
    }
    return null;
  } catch (error) {
    console.error('Error getting user role:', error);
    return null;
  }
}

/**
 * Check if user has a specific role
 */
export async function hasRole(role: UserRole): Promise<boolean> {
  const userRole = await getUserRole();
  return userRole === role;
}

/**
 * Check if user has any of the specified roles
 */
export async function hasAnyRole(roles: UserRole[]): Promise<boolean> {
  const userRole = await getUserRole();
  return userRole !== null && roles.includes(userRole);
}

/**
 * Check if user is admin
 */
export async function isAdmin(): Promise<boolean> {
  return hasRole('admin');
}

/**
 * Check if user can create articles (admin or project_lead)
 */
export async function canCreateArticles(): Promise<boolean> {
  return hasAnyRole(['admin', 'project_lead']);
}

/**
 * Check if user can add comments (admin or project_lead)
 */
export async function canAddComments(): Promise<boolean> {
  return hasAnyRole(['admin', 'project_lead']);
}

/**
 * Check if user can delete articles (admin only)
 */
export async function canDeleteArticles(): Promise<boolean> {
  return hasRole('admin');
}

/**
 * Check if user can manage users (admin only)
 */
export async function canManageUsers(): Promise<boolean> {
  return hasRole('admin');
}

/**
 * Get role display name
 */
export function getRoleDisplayName(role: UserRole): string {
  const roleNames: Record<string, string> = {
    admin: 'Admin',
    project_lead: 'Project Lead',
    team_member: 'Team Member',
  };
  return roleNames[role || ''] || 'No Role';
}




