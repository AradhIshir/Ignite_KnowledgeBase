import { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { upsertKnowledge, listUsers, createUser, deleteUser, updateUserRole } from '../../lib/api';
import { supabase } from '../../lib/supabaseClient';
import { isAdmin, getRoleDisplayName, type UserRole } from '../../lib/roles';
import MainMenu from '../../components/MainMenu';

const schema = z.object({
  summary: z.string().min(4),
  topics: z.string().optional(),
  decisions: z.string().optional(),
  faqs: z.string().optional(),
  source: z.string().optional(),
  date: z.string().optional(),
  project: z.string().optional(),
  raw_text: z.string().optional()
});
type FormValues = z.infer<typeof schema>;

const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  fullName: z.string().min(2),
  role: z.enum(['admin', 'project_lead', 'team_member'])
});
type UserFormValues = z.infer<typeof userSchema>;

const Container = styled.div`
  min-height: 100vh;
  background: linear-gradient(180deg, #E6F4F1 0%, #EAF3FF 100%);
`;

const Shell = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Tabs = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e5e7eb;
`;

const Tab = styled.button<{ $active: boolean }>`
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 3px solid ${props => props.$active ? '#1D74F5' : 'transparent'};
  color: ${props => props.$active ? '#1D74F5' : '#6b7280'};
  font-weight: ${props => props.$active ? 600 : 400};
  cursor: pointer;
  font-size: 1rem;
  
  &:hover {
    color: #1D74F5;
  }
`;

const Section = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  color: #1f2937;
  margin: 0 0 24px 0;
  font-size: 1.5rem;
`;

const Field = styled.div`
  display: grid;
  gap: 6px;
  margin-bottom: 12px;
`;

const Label = styled.label`
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
`;

const Input = styled.input`
  padding: 10px 12px;
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: ${(p) => p.theme.radii.md};
  background: ${(p) => p.theme.colors.surface};
  color: ${(p) => p.theme.colors.text};
  font-size: 0.875rem;
`;

const Select = styled.select`
  padding: 10px 12px;
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: ${(p) => p.theme.radii.md};
  background: ${(p) => p.theme.colors.surface};
  color: ${(p) => p.theme.colors.text};
  font-size: 0.875rem;
`;

const Textarea = styled.textarea`
  padding: 10px 12px;
  min-height: 120px;
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: ${(p) => p.theme.radii.md};
  background: ${(p) => p.theme.colors.surface};
  color: ${(p) => p.theme.colors.text};
  font-size: 0.875rem;
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: ${(p) => p.theme.radii.lg};
  background: #1D74F5;
  color: white;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  
  &:hover {
    background: #1565D8;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const DeleteButton = styled.button`
  padding: 8px 16px;
  border-radius: 8px;
  background: #dc2626;
  color: white;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
  
  &:hover {
    background: #b91c1c;
  }
`;

const ErrorMsg = styled.div`
  color: #D92D20;
  font-size: 14px;
`;

const SuccessMsg = styled.div`
  color: #059669;
  font-size: 14px;
  background: #D1FAE5;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
`;

const UsersTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
`;

const TableHeader = styled.thead`
  background: #f9fafb;
`;

const TableRow = styled.tr`
  border-bottom: 1px solid #e5e7eb;
  
  &:hover {
    background: #f9fafb;
  }
`;

const TableCell = styled.td`
  padding: 12px;
  font-size: 0.875rem;
`;

const TableHeaderCell = styled.th`
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
`;

const RoleBadge = styled.span<{ $role: UserRole }>`
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  background: ${props => {
    if (props.$role === 'admin') return '#fee2e2';
    if (props.$role === 'project_lead') return '#dbeafe';
    return '#e0e7ff';
  }};
  color: ${props => {
    if (props.$role === 'admin') return '#991b1b';
    if (props.$role === 'project_lead') return '#1e40af';
    return '#3730a3';
  }};
`;

const ActionCell = styled(TableCell)`
  display: flex;
  gap: 8px;
  align-items: center;
`;

interface User {
  id: string;
  email: string;
  full_name?: string;
  role: UserRole;
  created_at: string;
}

export default function Admin() {
  const [activeTab, setActiveTab] = useState<'articles' | 'users'>('articles');
  const { register: registerArticle, handleSubmit: handleArticleSubmit, reset: resetArticle, formState: { errors: articleErrors } } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const { register: registerUser, handleSubmit: handleUserSubmit, reset: resetUser, formState: { errors: userErrors } } = useForm<UserFormValues>({ resolver: zodResolver(userSchema) });
  
  const [articleInfo, setArticleInfo] = useState<string | null>(null);
  const [articleError, setArticleError] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<string | null>(null);
  const [userError, setUserError] = useState<string | null>(null);
  const [allowed, setAllowed] = useState<boolean>(false);
  const [users, setUsers] = useState<User[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submittingArticle, setSubmittingArticle] = useState(false);

  useEffect(() => {
    checkAdminAccess();
    if (activeTab === 'users') {
      fetchUsers();
    }
  }, [activeTab]);

  const checkAdminAccess = async () => {
    const isAdminUser = await isAdmin();
    setAllowed(isAdminUser);
  };

  const fetchUsers = async () => {
    try {
      setLoadingUsers(true);
      setUserError(null);
      setUserInfo(null);
      
      const usersList = await listUsers();
      setUsers(usersList);
    } catch (err: any) {
      console.error('Error fetching users:', err);
      setUserError(err.message || 'Failed to fetch users. Make sure the backend is running and configured.');
    } finally {
      setLoadingUsers(false);
    }
  };

  const onArticleSubmit = async (values: FormValues) => {
    try {
      setArticleInfo(null);
      setArticleError(null);
      setSubmittingArticle(true);
      
      const payload = {
        summary: values.summary,
        topics: values.topics ? values.topics.split(',').map(s => s.trim()).filter(Boolean) : null,
        decisions: values.decisions ? values.decisions.split('\n').filter(Boolean) : null,
        faqs: values.faqs ? values.faqs.split('\n').filter(Boolean) : null,
        source: values.source || null,
        date: values.date || null,
        project: values.project || null,
        raw_text: values.raw_text || null
      };
      
      await upsertKnowledge(payload);
      setArticleInfo('Article saved successfully!');
      resetArticle();
      setTimeout(() => setArticleInfo(null), 3000);
    } catch (err: any) {
      console.error('Error saving article:', err);
      let errorMessage = 'Failed to save article. Please try again.';
      
      if (err.message) {
        errorMessage = err.message;
      } else if (err.error) {
        errorMessage = err.error;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      setArticleError(errorMessage);
      setTimeout(() => setArticleError(null), 5000);
    } finally {
      setSubmittingArticle(false);
    }
  };

  const onUserSubmit = async (values: UserFormValues) => {
    try {
      setUserError(null);
      setUserInfo(null);
      setSubmitting(true);

      const newUser = await createUser({
        email: values.email,
        password: values.password,
        full_name: values.fullName,
        role: values.role,
      });

      setUserInfo(`User ${values.email} created successfully with role: ${getRoleDisplayName(values.role)}`);
      resetUser();
      await fetchUsers();
      setTimeout(() => setUserInfo(null), 3000);
    } catch (err: any) {
      console.error('Error creating user:', err);
      setUserError(err.message || 'Failed to create user. Make sure the backend is running and configured.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteUser = async (userId: string, userEmail: string) => {
    if (!confirm(`Are you sure you want to delete user ${userEmail}? This action cannot be undone.`)) {
      return;
    }

    try {
      setUserError(null);
      setUserInfo(null);
      
      await deleteUser(userId);
      setUserInfo(`User ${userEmail} deleted successfully`);
      await fetchUsers();
      setTimeout(() => setUserInfo(null), 3000);
    } catch (err: any) {
      console.error('Error deleting user:', err);
      setUserError(err.message || 'Failed to delete user. Make sure the backend is running and configured.');
    }
  };

  const handleChangeRole = async (userId: string, newRole: UserRole) => {
    try {
      setUserError(null);
      setUserInfo(null);
      
      await updateUserRole(userId, newRole);
      setUserInfo(`User role updated to ${getRoleDisplayName(newRole)}`);
      await fetchUsers();
      setTimeout(() => setUserInfo(null), 3000);
    } catch (err: any) {
      console.error('Error updating role:', err);
      setUserError(err.message || 'Failed to update user role. Make sure the backend is running and configured.');
    }
  };

  if (!allowed) {
    return (
      <>
        <MainMenu />
        <Container>
          <Shell>
            <Section>
              <h2>Access Denied</h2>
              <p>Only administrators can access this page.</p>
            </Section>
          </Shell>
        </Container>
      </>
    );
  }

  return (
    <>
      <MainMenu />
      <Container>
        <Shell>
          <Tabs>
            <Tab $active={activeTab === 'articles'} onClick={() => setActiveTab('articles')}>
              Add Article
            </Tab>
            <Tab $active={activeTab === 'users'} onClick={() => setActiveTab('users')}>
              Users
            </Tab>
          </Tabs>

          {activeTab === 'articles' && (
            <Section>
              <SectionTitle>Add Knowledge Item</SectionTitle>
              {articleInfo && <SuccessMsg>{articleInfo}</SuccessMsg>}
              {articleError && <ErrorMsg>{articleError}</ErrorMsg>}
              <form onSubmit={handleArticleSubmit(onArticleSubmit)}>
                <Field>
                  <Label>Summary *</Label>
                  <Input {...registerArticle('summary')} />
                  {articleErrors.summary && <ErrorMsg>{articleErrors.summary.message}</ErrorMsg>}
                </Field>
                <Field>
                  <Label>Topics (comma separated)</Label>
                  <Input {...registerArticle('topics')} />
                </Field>
                <Field>
                  <Label>Decisions (one per line)</Label>
                  <Textarea {...registerArticle('decisions')} />
                </Field>
                <Field>
                  <Label>FAQs (one per line)</Label>
                  <Textarea {...registerArticle('faqs')} />
                </Field>
                <Field>
                  <Label>Source</Label>
                  <Input {...registerArticle('source')} />
                </Field>
                <Field>
                  <Label>Date</Label>
                  <Input type="date" {...registerArticle('date')} />
                </Field>
                <Field>
                  <Label>Project</Label>
                  <Input {...registerArticle('project')} />
                </Field>
                <Field>
                  <Label>Original content</Label>
                  <Textarea {...registerArticle('raw_text')} />
                </Field>
                <Button type="submit" disabled={submittingArticle}>
                  {submittingArticle ? 'Saving...' : 'Save Article'}
                </Button>
              </form>
            </Section>
          )}

          {activeTab === 'users' && (
            <Section>
              <SectionTitle>User Management</SectionTitle>
              
              {userInfo && <SuccessMsg>{userInfo}</SuccessMsg>}
              {userError && <ErrorMsg>{userError}</ErrorMsg>}

              <h3 style={{ marginTop: '24px', marginBottom: '16px', fontSize: '1.125rem' }}>Add New User</h3>
              <form onSubmit={handleUserSubmit(onUserSubmit)}>
                <Field>
                  <Label>Full Name *</Label>
                  <Input {...registerUser('fullName')} placeholder="John Doe" />
                  {userErrors.fullName && <ErrorMsg>{userErrors.fullName.message}</ErrorMsg>}
                </Field>
                <Field>
                  <Label>Email *</Label>
                  <Input type="email" {...registerUser('email')} placeholder="user@example.com" />
                  {userErrors.email && <ErrorMsg>{userErrors.email.message}</ErrorMsg>}
                </Field>
                <Field>
                  <Label>Password *</Label>
                  <Input type="password" {...registerUser('password')} placeholder="Minimum 6 characters" />
                  {userErrors.password && <ErrorMsg>{userErrors.password.message}</ErrorMsg>}
                </Field>
                <Field>
                  <Label>Role *</Label>
                  <Select {...registerUser('role')}>
                    <option value="team_member">Team Member (Read-only)</option>
                    <option value="project_lead">Project Lead (Can add articles & comments)</option>
                    <option value="admin">Admin (Full access)</option>
                  </Select>
                  {userErrors.role && <ErrorMsg>{userErrors.role.message}</ErrorMsg>}
                </Field>
                <Button type="submit" disabled={submitting}>
                  {submitting ? 'Creating...' : 'Create User'}
                </Button>
              </form>

              <h3 style={{ marginTop: '32px', marginBottom: '16px', fontSize: '1.125rem' }}>All Users</h3>
              {loadingUsers ? (
                <p>Loading users...</p>
              ) : users.length === 0 ? (
                <p style={{ color: '#6b7280' }}>No users found. Create your first user above.</p>
              ) : (
                <UsersTable>
                  <TableHeader>
                    <tr>
                      <TableHeaderCell>Name</TableHeaderCell>
                      <TableHeaderCell>Email</TableHeaderCell>
                      <TableHeaderCell>Role</TableHeaderCell>
                      <TableHeaderCell>Created</TableHeaderCell>
                      <TableHeaderCell>Actions</TableHeaderCell>
                    </tr>
                  </TableHeader>
                  <tbody>
                    {users.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>{user.full_name || 'N/A'}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>
                          <RoleBadge $role={user.role}>{getRoleDisplayName(user.role)}</RoleBadge>
                        </TableCell>
                        <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                        <ActionCell>
                          <Select
                            value={user.role || 'team_member'}
                            onChange={(e) => handleChangeRole(user.id, e.target.value as UserRole)}
                            style={{ padding: '6px 12px', fontSize: '0.75rem' }}
                          >
                            <option value="team_member">Team Member</option>
                            <option value="project_lead">Project Lead</option>
                            <option value="admin">Admin</option>
                          </Select>
                          <DeleteButton onClick={() => handleDeleteUser(user.id, user.email)}>
                            Delete
                          </DeleteButton>
                        </ActionCell>
                      </TableRow>
                    ))}
                  </tbody>
                </UsersTable>
              )}
            </Section>
          )}
        </Shell>
      </Container>
    </>
  );
}
