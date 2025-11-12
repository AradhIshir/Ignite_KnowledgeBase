import { useEffect, useState } from 'react';
import styled from 'styled-components';
import { supabase } from '../../lib/supabaseClient';
import Link from 'next/link';
import MainMenu from '../../components/MainMenu';

// Decode HTML entities
const decodeHtmlEntities = (text: string): string => {
  if (!text) return '';
  if (typeof window === 'undefined') {
    // Server-side: decode common entities
    const entityMap: { [key: string]: string } = {
      '&amp;': '&',
      '&lt;': '<',
      '&gt;': '>',
      '&quot;': '"',
      '&#39;': "'",
      '&apos;': "'",
      '&nbsp;': ' ',
      '&middot;': '·',
      '&copy;': '©',
      '&reg;': '®',
      '&trade;': '™',
      '&hellip;': '…',
      '&mdash;': '—',
      '&ndash;': '–',
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

// Strip HTML tags for preview
const stripHtmlTags = (html: string): string => {
  if (!html) return '';
  return html.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
};

// Header Components
const Header = styled.header`
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background: #1D74F5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
`;

const LogoText = styled.div`
  display: flex;
  flex-direction: column;
`;

const LogoTitle = styled.h1`
  font-size: 18px;
  font-weight: 700;
  color: #1D74F5;
  margin: 0;
`;

const LogoSubtitle = styled.p`
  font-size: 12px;
  color: #6B7280;
  margin: 0;
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 24px;
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;

  &:hover {
    background-color: #f3f4f6;
  }
`;

const UserProfile = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const UserAvatar = styled.div`
  width: 32px;
  height: 32px;
  background: #1D74F5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
`;

// Main Dashboard Components
const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
`;

const Title = styled.h1`
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TitleBlue = styled.span`
  color: #1D74F5;
`;

const TitleGreen = styled.span`
  color: #22C7A9;
`;

const Tagline = styled.p`
  color: #6B7280;
  font-size: 16px;
  margin: 0 0 32px 0;
`;

const ActionBar = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
`;

const ActionButtons = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ViewToggle = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  color: #374151;
  cursor: pointer;
  font-size: 14px;

  &:hover {
    background: #f9fafb;
  }
`;

const ExportButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  color: #374151;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;

  &:hover {
    background: #f9fafb;
  }
`;

const NewArticleButton = styled(Link)`
  display: flex;
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

// Summary Cards
const SummaryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
`;

const SummaryCard = styled.div<{ $bgColor: string }>`
  background: ${props => props.$bgColor};
  border-radius: 12px;
  padding: 24px;
  color: white;
  position: relative;
  overflow: hidden;
`;

const SummaryLabel = styled.div`
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  opacity: 0.9;
`;

const SummaryValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 16px;
`;

const SummaryIcon = styled.div`
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 32px;
  opacity: 0.3;
`;

// Search and Filters
const SearchSection = styled.div`
  margin-bottom: 32px;
`;

const SearchBar = styled.div`
  position: relative;
  margin-bottom: 16px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 48px;
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

const SearchIcon = styled.div`
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #6B7280;
`;

const Filters = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const FilterLabel = styled.span`
  font-weight: 500;
  color: #374151;
`;

const FilterSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  font-size: 14px;
  min-width: 150px;
`;

// Knowledge Items Grid
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

const ViewDetailsButton = styled.button`
  width: 100%;
  padding: 12px 16px;
  background: #1D74F5;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.2s;

  &:hover {
    background: #1d5bb8;
  }
`;

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalArticles: 0,
    projects: 0,
    topics: 0
  });
  const [knowledgeItems, setKnowledgeItems] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProject, setSelectedProject] = useState('all');
  const [selectedTopic, setSelectedTopic] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch knowledge items
        const { data: items, error } = await supabase
          .from('knowledge_items')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) throw error;

        setKnowledgeItems(items || []);

        // Calculate stats
        const uniqueProjects = new Set(items?.map(item => item.project).filter(Boolean));
        const allTopics = items?.flatMap(item => item.topics || []);
        const uniqueTopics = new Set(allTopics);

        setStats({
          totalArticles: items?.length || 0,
          projects: uniqueProjects.size,
          topics: uniqueTopics.size
        });
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const filteredItems = knowledgeItems.filter(item => {
    const matchesSearch = !searchTerm || 
      item.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.raw_text && item.raw_text.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesProject = selectedProject === 'all' || item.project === selectedProject;
    const matchesTopic = selectedTopic === 'all' || 
      (item.topics && item.topics.includes(selectedTopic));

    return matchesSearch && matchesProject && matchesTopic;
  });

  const handleExportCSV = () => {
    const csvContent = [
      ['Title', 'Summary', 'Project', 'Topics', 'Date', 'Source'],
      ...filteredItems.map(item => [
        item.summary,
        item.raw_text || '',
        item.project || '',
        (item.topics || []).join('; '),
        item.date || '',
        item.source || ''
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'knowledge-base-export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <>
      <MainMenu />
      <Container>
        <Title>
          <TitleBlue>Knowledge</TitleBlue> <TitleGreen>Base</TitleGreen>
        </Title>
        <Tagline>Explore and discover team insights</Tagline>

        <ActionBar>
          <div></div>
          <ActionButtons>
            <ViewToggle>
              ☰ View
            </ViewToggle>
            <ExportButton onClick={handleExportCSV}>
              📥 Export CSV
            </ExportButton>
            <NewArticleButton href="/app/items/new">
              ➕ New Article
            </NewArticleButton>
          </ActionButtons>
        </ActionBar>

        <SummaryGrid>
          <SummaryCard $bgColor="#1D74F5">
            <SummaryLabel>Total Articles</SummaryLabel>
            <SummaryValue>{stats.totalArticles}</SummaryValue>
            <SummaryIcon>📚</SummaryIcon>
          </SummaryCard>
          <SummaryCard $bgColor="#22C7A9">
            <SummaryLabel>Projects</SummaryLabel>
            <SummaryValue>{stats.projects}</SummaryValue>
            <SummaryIcon>📈</SummaryIcon>
          </SummaryCard>
          <SummaryCard $bgColor="#EC4899">
            <SummaryLabel>Topics</SummaryLabel>
            <SummaryValue>{stats.topics}</SummaryValue>
            <SummaryIcon>⭐</SummaryIcon>
          </SummaryCard>
        </SummaryGrid>

        <SearchSection>
          <SearchBar>
            <SearchIcon>🔍</SearchIcon>
            <SearchInput
              type="text"
              placeholder="Search articles by title, summary, or content..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </SearchBar>
          
          <Filters>
            <FilterLabel>Filters:</FilterLabel>
            <FilterSelect 
              value={selectedProject} 
              onChange={(e) => setSelectedProject(e.target.value)}
            >
              <option value="all">All Projects</option>
              {Array.from(new Set(knowledgeItems.map(item => item.project).filter(Boolean))).map(project => (
                <option key={project} value={project}>{project}</option>
              ))}
            </FilterSelect>
            <FilterSelect 
              value={selectedTopic} 
              onChange={(e) => setSelectedTopic(e.target.value)}
            >
              <option value="all">All Topics</option>
              {Array.from(new Set(knowledgeItems.flatMap(item => item.topics || []))).map(topic => (
                <option key={topic} value={topic}>{topic}</option>
              ))}
            </FilterSelect>
          </Filters>
        </SearchSection>

        <ItemsGrid>
          {filteredItems.map((item) => {
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

            // Get clean preview text (decode HTML entities and strip HTML for Confluence)
            const getPreviewText = () => {
              if (item.source === 'confluence' && item.raw_text) {
                // For Confluence, extract text from HTML
                const text = stripHtmlTags(item.raw_text);
                return decodeHtmlEntities(text).substring(0, 150) + (text.length > 150 ? '...' : '');
              }
              const summary = item.summary || item.raw_text?.substring(0, 100) || 'No description available';
              return decodeHtmlEntities(summary);
            };

            return (
            <ItemCard key={item.id}>
              <ItemTitle>{getCardTitle()}</ItemTitle>
              <ItemDescription>{getPreviewText()}</ItemDescription>
              <ItemMetadata>
                <MetadataItem>
                  📄 {item.project || 'FS'}
                </MetadataItem>
                <MetadataItem>
                  📅 {new Date(item.created_at).toLocaleDateString()}
                </MetadataItem>
                <MetadataItem>
                  {item.source === 'confluence' ? '📄' : item.source === 'slack' ? '💬' : '📄'} {item.source || 'slack'}
                </MetadataItem>
              </ItemMetadata>
              <ViewDetailsButton as={Link} href={`/app/items/${item.id}`}>
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

