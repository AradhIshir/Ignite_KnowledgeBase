import { useEffect, useState } from 'react';
import styled from 'styled-components';
import { supabase } from '../../../lib/supabaseClient';
import Link from 'next/link';
import MainMenu from '../../../components/MainMenu';

const Container = styled.div`
  max-width: 1200px;
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

const ItemsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
`;

const ItemCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

const ItemTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #1D74F5;
  margin: 0 0 8px 0;
`;

const ItemDescription = styled.p`
  color: #6B7280;
  font-size: 14px;
  margin: 0 0 16px 0;
  line-height: 1.5;
  word-wrap: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  max-width: 100%;
`;

const ItemMetadata = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  font-size: 12px;
  color: #6B7280;
`;

const MetadataItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const ViewDetailsButton = styled(Link)`
  display: block;
  width: 100%;
  padding: 12px 16px;
  background: #1D74F5;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  text-align: center;
  transition: background-color 0.2s;

  &:hover {
    background: #1d5bb8;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 64px 24px;
  color: #6B7280;
`;

const EmptyTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
`;

const EmptyDescription = styled.p`
  font-size: 16px;
  margin: 0 0 24px 0;
`;

const CreateButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: #22C7A9;
  color: white;
  border: none;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #1ea085;
  }
`;

export default function ItemsList() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const { data, error } = await supabase
          .from('knowledge_items')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) throw error;
        setItems(data || []);
      } catch (error) {
        console.error('Error fetching items:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, []);

  if (loading) {
    return (
      <Container>
        <Header>
          <Title>Knowledge Items</Title>
          <Subtitle>All articles in your knowledge base</Subtitle>
        </Header>
        <div>Loading...</div>
      </Container>
    );
  }

  if (items.length === 0) {
    return (
      <Container>
        <Header>
          <Title>Knowledge Items</Title>
          <Subtitle>All articles in your knowledge base</Subtitle>
        </Header>
        <EmptyState>
          <EmptyTitle>No articles yet</EmptyTitle>
          <EmptyDescription>
            Start building your team's knowledge base by creating your first article.
          </EmptyDescription>
          <CreateButton href="/app/items/new">
            ➕ Create First Article
          </CreateButton>
        </EmptyState>
      </Container>
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
              <Title>Knowledge Items</Title>
              <Subtitle>All articles in your knowledge base</Subtitle>
            </div>
          </HeaderLeft>
          <HeaderRight>
            <ActionButton href="/app/dashboard">🏠 Dashboard</ActionButton>
            <ActionButton href="/app/items/new" variant="primary">➕ New Article</ActionButton>
          </HeaderRight>
        </Header>
        
        <ItemsGrid>
          {items.map((item) => {
            // Generate title: "Keyword" only for Slack, actual title for Confluence
            const getCardTitle = () => {
              if (item.source === 'confluence') {
                // For Confluence, the summary field contains the actual page title
                return decodeHtmlEntities(item.summary || 'Confluence Article');
              }
              if (item.topics && item.topics.length > 0) {
                const keyword = item.topics[0];
                const keywordTitle = keyword.split(' ').map(word => 
                  word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
                ).join(' ');
                return keywordTitle;
              }
              return item.summary || 'Article';
            };

            // Decode HTML entities and strip HTML for preview
            const decodeHtmlEntities = (text: string): string => {
              if (!text) return '';
              if (typeof window === 'undefined') {
                const entityMap: { [key: string]: string } = {
                  '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'",
                  '&apos;': "'", '&nbsp;': ' ', '&middot;': '·', '&copy;': '©',
                  '&reg;': '®', '&trade;': '™', '&hellip;': '…', '&mdash;': '—', '&ndash;': '–',
                };
                let decoded = text;
                for (const [entity, char] of Object.entries(entityMap)) {
                  decoded = decoded.replace(new RegExp(entity, 'g'), char);
                }
                decoded = decoded.replace(/&#(\d+);/g, (match, dec) => String.fromCharCode(parseInt(dec, 10)));
                decoded = decoded.replace(/&#x([a-f\d]+);/gi, (match, hex) => String.fromCharCode(parseInt(hex, 16)));
                return decoded;
              } else {
                const textarea = document.createElement('textarea');
                textarea.innerHTML = text;
                return textarea.value;
              }
            };

            const stripHtmlTags = (html: string): string => {
              if (!html) return '';
              return html.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
            };

            const getPreviewText = () => {
              if (item.source === 'confluence' && item.raw_text) {
                const text = stripHtmlTags(item.raw_text);
                return decodeHtmlEntities(text).substring(0, 150) + (text.length > 150 ? '...' : '');
              }
              const summary = item.summary || item.raw_text?.substring(0, 150) || 'No description available';
              return decodeHtmlEntities(summary);
            };

            return (
            <ItemCard key={item.id}>
              <ItemTitle>{getCardTitle()}</ItemTitle>
              <ItemDescription>{getPreviewText()}</ItemDescription>
              <ItemMetadata>
                <MetadataItem>
                  📄 {item.project || 'General'}
                </MetadataItem>
                <MetadataItem>
                  📅 {new Date(item.created_at).toLocaleDateString()}
                </MetadataItem>
                <MetadataItem>
                  {item.source === 'confluence' ? '📄' : item.source === 'slack' ? '💬' : '📄'} {item.source || 'Unknown'}
                </MetadataItem>
              </ItemMetadata>
              <ViewDetailsButton href={`/app/items/${item.id}`}>
                👁️ View Details
              </ViewDetailsButton>
            </ItemCard>
            );
          })}
        </ItemsGrid>
      </Container>
    </>
  );
}