import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import styled from 'styled-components';
import { supabase } from '../../../lib/supabaseClient';
import Link from 'next/link';
import MainMenu from '../../../components/MainMenu';

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

const Title = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #1D74F5;
  margin: 0;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled(Link)<{ variant?: 'primary' | 'secondary' }>`
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

const ArticleCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const ArticleTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #1D74F5;
  margin: 0 0 16px 0;
`;

const ArticleContent = styled.div`
  color: #374151;
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 24px;
  white-space: pre-wrap;
`;

const Metadata = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const MetadataItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const MetadataLabel = styled.span`
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const MetadataValue = styled.span`
  font-size: 14px;
  color: #374151;
`;

const TagsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
`;

const Tag = styled.span`
  background: #f3f4f6;
  color: #374151;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
`;

const Section = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 12px 0;
`;

const List = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const ListItem = styled.li`
  background: #f9fafb;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  color: #374151;
  font-size: 14px;
  line-height: 1.5;
`;

const LoadingState = styled.div`
  text-align: center;
  padding: 64px 24px;
  color: #6B7280;
`;

const ErrorState = styled.div`
  text-align: center;
  padding: 64px 24px;
  color: #dc2626;
`;

const BackButton = styled(Link)`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6B7280;
  text-decoration: none;
  font-size: 14px;
  margin-bottom: 16px;

  &:hover {
    color: #374151;
  }
`;

export default function ArticleDetails() {
  const router = useRouter();
  const { id } = router.query;
  const [article, setArticle] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      fetchArticle();
    }
  }, [id]);

  const fetchArticle = async () => {
    try {
      const { data, error } = await supabase
        .from('knowledge_items')
        .select('*')
        .eq('id', id)
        .single();

      if (error) throw error;
      setArticle(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load article');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <BackButton href="/app/dashboard">← Back to Dashboard</BackButton>
        <LoadingState>Loading article...</LoadingState>
      </Container>
    );
  }

  if (error || !article) {
    return (
      <Container>
        <BackButton href="/app/dashboard">← Back to Dashboard</BackButton>
        <ErrorState>
          <h2>Article not found</h2>
          <p>{error || 'The article you are looking for does not exist.'}</p>
          <ButtonGroup>
            <Button href="/app/dashboard">← Back to Dashboard</Button>
            <Button href="/app/items">View All Articles</Button>
          </ButtonGroup>
        </ErrorState>
      </Container>
    );
  }

  return (
    <>
      <MainMenu />
      <Container>
        <BackButton href="/app/dashboard">← Back to Dashboard</BackButton>
      
      <Header>
        <Title>Article Details</Title>
        <ButtonGroup>
          <Button href="/app/dashboard">🏠 Dashboard</Button>
          <Button href="/app/items">📖 All Articles</Button>
        </ButtonGroup>
      </Header>

      <ArticleCard>
        <ArticleTitle>{article.summary}</ArticleTitle>
        
        <ArticleContent>{article.raw_text}</ArticleContent>

        <Metadata>
          <MetadataItem>
            <MetadataLabel>Project</MetadataLabel>
            <MetadataValue>{article.project || 'General'}</MetadataValue>
          </MetadataItem>
          <MetadataItem>
            <MetadataLabel>Source</MetadataLabel>
            <MetadataValue>{article.source || 'Unknown'}</MetadataValue>
          </MetadataItem>
          <MetadataItem>
            <MetadataLabel>Date</MetadataLabel>
            <MetadataValue>{new Date(article.created_at).toLocaleDateString()}</MetadataValue>
          </MetadataItem>
          <MetadataItem>
            <MetadataLabel>Created By</MetadataLabel>
            <MetadataValue>{article.created_by ? 'User' : 'System'}</MetadataValue>
          </MetadataItem>
        </Metadata>

        {article.topics && article.topics.length > 0 && (
          <Section>
            <SectionTitle>Topics</SectionTitle>
            <TagsContainer>
              {article.topics.map((topic: string, index: number) => (
                <Tag key={index}>{topic}</Tag>
              ))}
            </TagsContainer>
          </Section>
        )}

        {article.decisions && article.decisions.length > 0 && (
          <Section>
            <SectionTitle>Key Decisions</SectionTitle>
            <List>
              {article.decisions.map((decision: string, index: number) => (
                <ListItem key={index}>{decision}</ListItem>
              ))}
            </List>
          </Section>
        )}

        {article.faqs && article.faqs.length > 0 && (
          <Section>
            <SectionTitle>Frequently Asked Questions</SectionTitle>
            <List>
              {article.faqs.map((faq: string, index: number) => (
                <ListItem key={index}>{faq}</ListItem>
              ))}
            </List>
          </Section>
        )}
      </ArticleCard>
    </Container>
    </>
  );
}