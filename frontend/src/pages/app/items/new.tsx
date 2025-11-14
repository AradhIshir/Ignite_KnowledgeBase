import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import styled from 'styled-components';
import { supabase } from '../../../lib/supabaseClient';
import Link from 'next/link';
import MainMenu from '../../../components/MainMenu';
import { canCreateArticles } from '../../../lib/roles';

const Container = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const BackButton = styled(Link)`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6B7280;
  text-decoration: none;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;

  &:hover {
    color: #374151;
    background: #f3f4f6;
  }
`;

const HeaderRight = styled.div`
  display: flex;
  gap: 12px;
`;

const ActionButton = styled(Link)<{ variant?: 'primary' | 'secondary' }>`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.2s;

  ${props => props.variant === 'primary' ? `
    background: #22C7A9;
    color: white;
    
    &:hover {
      background: #1ea085;
    }
  ` : `
    background: white;
    color: #374151;
    border: 1px solid #d1d5db;
    
    &:hover {
      background: #f9fafb;
    }
  `}
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #1D74F5;
  margin: 0 0 8px 0;
`;

const Subtitle = styled.p`
  color: #6B7280;
  font-size: 16px;
  margin: 0;
`;

const Form = styled.form`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const FormGroup = styled.div`
  margin-bottom: 24px;
`;

const Label = styled.label`
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  background: white;

  &:focus {
    outline: none;
    border-color: #1D74F5;
    box-shadow: 0 0 0 3px rgba(29, 116, 245, 0.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  min-height: 120px;
  resize: vertical;

  &:focus {
    outline: none;
    border-color: #1D74F5;
    box-shadow: 0 0 0 3px rgba(29, 116, 245, 0.1);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  background: white;

  &:focus {
    outline: none;
    border-color: #1D74F5;
    box-shadow: 0 0 0 3px rgba(29, 116, 245, 0.1);
  }
`;

const TagInput = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  background: white;

  &:focus {
    outline: none;
    border-color: #1D74F5;
    box-shadow: 0 0 0 3px rgba(29, 116, 245, 0.1);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 32px;
`;

const Button = styled.button<{ variant?: 'primary' | 'secondary' }>`
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;

  ${props => props.variant === 'primary' ? `
    background: #1D74F5;
    color: white;
    
    &:hover {
      background: #1d5bb8;
    }
  ` : `
    background: white;
    color: #374151;
    border: 1px solid #d1d5db;
    
    &:hover {
      background: #f9fafb;
    }
  `}
`;

const ErrorMessage = styled.div`
  color: #dc2626;
  font-size: 14px;
  margin-top: 8px;
`;

const SuccessMessage = styled.div`
  color: #059669;
  font-size: 14px;
  margin-top: 8px;
`;

export default function NewArticle() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    summary: '',
    raw_text: '',
    project: '',
    source: '',
    date: new Date().toISOString().split('T')[0],
    topics: '',
    decisions: '',
    faqs: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  useEffect(() => {
    checkPermission();
  }, []);

  const checkPermission = async () => {
    const canCreate = await canCreateArticles();
    setHasPermission(canCreate);
    if (!canCreate) {
      setError('Only Admins and Project Leads can create articles.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        throw new Error('You must be logged in to create articles');
      }

      const articleData = {
        ...formData,
        topics: formData.topics ? formData.topics.split(',').map(t => t.trim()).filter(Boolean) : [],
        decisions: formData.decisions ? formData.decisions.split(',').map(d => d.trim()).filter(Boolean) : [],
        faqs: formData.faqs ? formData.faqs.split(',').map(f => f.trim()).filter(Boolean) : [],
        created_by: user.id
      };

      const { error } = await supabase
        .from('knowledge_items')
        .insert([articleData]);

      if (error) throw error;

      setSuccess('Article created successfully!');
      setTimeout(() => {
        router.push('/app/dashboard');
      }, 1500);
    } catch (err: any) {
      let errorMessage = 'Failed to create article. Please try again.';
      
      if (err.message) {
        errorMessage = err.message;
      } else if (err.error) {
        errorMessage = err.error;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      // Provide more specific error messages
      if (errorMessage.includes('permission') || errorMessage.includes('role')) {
        errorMessage = 'You do not have permission to create articles. Only Admins and Project Leads can create articles.';
      } else if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
        errorMessage = 'Network error. Please check your internet connection and try again.';
      } else if (errorMessage.includes('authentication') || errorMessage.includes('login')) {
        errorMessage = 'You must be logged in to create articles. Please log in and try again.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (hasPermission === false) {
    return (
      <>
        <MainMenu />
        <Container>
          <Header>
            <HeaderLeft>
              <BackButton href="/app/dashboard">← Back to Dashboard</BackButton>
              <div>
                <Title>Access Denied</Title>
                <Subtitle>Only Admins and Project Leads can create articles.</Subtitle>
              </div>
            </HeaderLeft>
          </Header>
          {error && <ErrorMessage>{error}</ErrorMessage>}
        </Container>
      </>
    );
  }

  return (
    <>
      <MainMenu />
      <Container>
        <Header>
          <HeaderLeft>
            <BackButton href="/app/dashboard">← Back to Dashboard</BackButton>
            <div>
              <Title>Create New Article</Title>
              <Subtitle>Add a new knowledge item to your team's knowledge base</Subtitle>
            </div>
          </HeaderLeft>
          <HeaderRight>
            <ActionButton href="/app/dashboard">🏠 Dashboard</ActionButton>
            <ActionButton href="/app/items">📖 All Articles</ActionButton>
          </HeaderRight>
        </Header>

      <Form onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="summary">Article Title *</Label>
          <Input
            type="text"
            id="summary"
            name="summary"
            value={formData.summary}
            onChange={handleChange}
            placeholder="Enter a clear, descriptive title"
            required
          />
        </FormGroup>

        <FormGroup>
          <Label htmlFor="raw_text">Content *</Label>
          <TextArea
            id="raw_text"
            name="raw_text"
            value={formData.raw_text}
            onChange={handleChange}
            placeholder="Write the main content of your article..."
            required
          />
        </FormGroup>

        <FormGroup>
          <Label htmlFor="project">Project</Label>
          <Input
            type="text"
            id="project"
            name="project"
            value={formData.project}
            onChange={handleChange}
            placeholder="e.g., Frontend Development, Backend API"
          />
        </FormGroup>

        <FormGroup>
          <Label htmlFor="source">Source</Label>
          <Select
            id="source"
            name="source"
            value={formData.source}
            onChange={handleChange}
          >
            <option value="">Select source</option>
            <option value="slack">Slack</option>
            <option value="email">Email</option>
            <option value="meeting">Meeting</option>
            <option value="documentation">Documentation</option>
            <option value="other">Other</option>
          </Select>
        </FormGroup>

        <FormGroup>
          <Label htmlFor="date">Date</Label>
          <Input
            type="date"
            id="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
          />
        </FormGroup>

        <FormGroup>
          <Label htmlFor="topics">Topics (comma-separated)</Label>
          <TagInput
            type="text"
            id="topics"
            name="topics"
            value={formData.topics}
            onChange={handleChange}
            placeholder="e.g., authentication, security, performance"
          />
        </FormGroup>

        <FormGroup>
          <Label htmlFor="decisions">Key Decisions (comma-separated)</Label>
          <TagInput
            type="text"
            id="decisions"
            name="decisions"
            value={formData.decisions}
            onChange={handleChange}
            placeholder="e.g., Use JWT for auth, Implement rate limiting"
          />
        </FormGroup>

        <FormGroup>
          <Label htmlFor="faqs">FAQs (comma-separated)</Label>
          <TagInput
            type="text"
            id="faqs"
            name="faqs"
            value={formData.faqs}
            onChange={handleChange}
            placeholder="e.g., How to reset password?, What is the API rate limit?"
          />
        </FormGroup>

        {error && <ErrorMessage>{error}</ErrorMessage>}
        {success && <SuccessMessage>{success}</SuccessMessage>}

        <ButtonGroup>
          <Button
            type="button"
            variant="secondary"
            onClick={() => router.push('/app/dashboard')}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Article'}
          </Button>
        </ButtonGroup>
      </Form>
    </Container>
    </>
  );
}
