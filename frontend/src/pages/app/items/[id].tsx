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

const ConfluenceContent = styled.div`
  color: #172b4d;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 24px;
  
  /* Confluence-like styling */
  h1, h2, h3, h4, h5, h6 {
    color: #172b4d;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 12px;
  }
  
  h1 { font-size: 28px; }
  h2 { font-size: 24px; }
  h3 { font-size: 20px; }
  h4 { font-size: 18px; }
  
  p {
    margin: 12px 0;
    color: #172b4d;
  }
  
  ul, ol {
    margin: 12px 0;
    padding-left: 24px;
  }
  
  li {
    margin: 6px 0;
    color: #172b4d;
  }
  
  strong {
    font-weight: 600;
    color: #172b4d;
  }
  
  em {
    font-style: italic;
  }
  
  code {
    background: #f4f5f7;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
  }
  
  pre {
    background: #f4f5f7;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    margin: 12px 0;
  }
  
  a {
    color: #0052cc;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
  
  blockquote {
    border-left: 3px solid #dfe1e6;
    padding-left: 16px;
    margin: 12px 0;
    color: #6b778c;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
  }
  
  th, td {
    border: 1px solid #dfe1e6;
    padding: 8px 12px;
    text-align: left;
  }
  
  th {
    background: #f4f5f7;
    font-weight: 600;
  }
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

  // Parse grouped messages from raw_text
  const parseMessages = (rawText: string) => {
    if (!rawText) return [];
    
    const messages: Array<{
      sender: string;
      text: string;
      date: string;
      attachments: Array<{name: string, url: string, type?: string, size?: number}>;
    }> = [];
    
    // Split by message separator (handles both "Message" and "Thread Reply" with/without date)
    // Format: "--- Message from Name on 10 Nov. ---" (new) or "--- Message from Name ---" (old)
    let messageBlocks: string[];
    let hasDates = rawText.includes(' on ');
    
    if (hasDates) {
      // New format with dates
      messageBlocks = rawText.split(/--- (?:Thread Reply|Message) from (.+?) on (.+?) ---/);
    } else {
      // Old format without dates (backward compatibility)
      messageBlocks = rawText.split(/--- (?:Thread Reply|Message) from (.+?) ---/);
    }
    
    // Process messages
    if (hasDates) {
      // First element is empty, then triplets of [sender, date, content]
      for (let i = 1; i < messageBlocks.length; i += 3) {
        if (i + 2 >= messageBlocks.length) break;
        
        const sender = messageBlocks[i].trim();
        const date = messageBlocks[i + 1].trim();
        const block = messageBlocks[i + 2];
        
        let text = '';
        const attachments: Array<{name: string, url: string}> = [];
        
        const lines = block.split('\n');
        for (let j = 0; j < lines.length; j++) {
          const line = lines[j].trim();
          if (!line || line.startsWith('_msg_hash:')) continue;
          
          if (line.startsWith('Message:')) {
            text = line.replace(/^Message:\s*/, '');
          } else if (line.startsWith('_attachments_json:')) {
            // Parse JSON attachments
            try {
              const jsonStr = line.replace(/^_attachments_json:\s*/, '');
              const parsedAttachments = JSON.parse(jsonStr);
              if (Array.isArray(parsedAttachments)) {
                parsedAttachments.forEach((att: any) => {
                  if (att.url) {
                    attachments.push({
                      name: att.name || 'Unknown',
                      url: att.url,
                      type: att.type || '',
                      size: att.size || 0
                    });
                  }
                });
              }
            } catch (e) {
              console.error('Failed to parse attachments JSON:', e);
            }
          } else if (line.startsWith('Attachments:')) {
            // Fallback: parse human-readable format if JSON not available
            if (attachments.length === 0) {
              const attachmentList = line.replace(/^Attachments:\s*/, '').split(';');
              attachmentList.forEach(att => {
                const match = att.trim().match(/^(.+?):\s*(.+)$/);
                if (match) {
                  attachments.push({ name: match[1].trim(), url: match[2].trim() });
                }
              });
            }
          } else if (text && !line.startsWith('_')) {
            // Append continuation lines to message text
            text += ' ' + line;
          }
        }
        
        if (text || attachments.length > 0) {
          messages.push({ sender, text: text.trim(), date, attachments });
        }
      }
    } else {
      // Old format: pairs of [sender, content]
      for (let i = 1; i < messageBlocks.length; i += 2) {
        if (i + 1 >= messageBlocks.length) break;
        
        const sender = messageBlocks[i].trim();
        const block = messageBlocks[i + 1];
        
        let text = '';
        const attachments: Array<{name: string, url: string}> = [];
        
        const lines = block.split('\n');
        for (let j = 0; j < lines.length; j++) {
          const line = lines[j].trim();
          if (!line || line.startsWith('_msg_hash:')) continue;
          
          if (line.startsWith('Message:')) {
            text = line.replace(/^Message:\s*/, '');
          } else if (line.startsWith('_attachments_json:')) {
            try {
              const jsonStr = line.replace(/^_attachments_json:\s*/, '');
              const parsedAttachments = JSON.parse(jsonStr);
              if (Array.isArray(parsedAttachments)) {
                parsedAttachments.forEach((att: any) => {
                  if (att.url) {
                    attachments.push({
                      name: att.name || 'Unknown',
                      url: att.url,
                      type: att.type || '',
                      size: att.size || 0
                    });
                  }
                });
              }
            } catch (e) {
              console.error('Failed to parse attachments JSON:', e);
            }
          } else if (line.startsWith('Attachments:')) {
            if (attachments.length === 0) {
              const attachmentList = line.replace(/^Attachments:\s*/, '').split(';');
              attachmentList.forEach(att => {
                const match = att.trim().match(/^(.+?):\s*(.+)$/);
                if (match) {
                  attachments.push({ name: match[1].trim(), url: match[2].trim() });
                }
              });
            }
          } else if (text && !line.startsWith('_')) {
            text += ' ' + line;
          }
        }
        
        if (text || attachments.length > 0) {
          messages.push({ sender, text: text.trim(), date: 'Unknown date', attachments });
        }
      }
    }
    
    return messages;
  };

  // Get page title: "Keyword" only (e.g., "Pending Approval")
  const getPageTitle = () => {
    if (article?.topics && article.topics.length > 0) {
      // Capitalize first letter of each word in keyword
      const keyword = article.topics[0];
      const keywordTitle = keyword.split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
      ).join(' ');
      return keywordTitle;
    }
    return article?.summary || 'Article Details';
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

  // Decode HTML entities (comprehensive)
  const decodeHtmlEntities = (text: string): string => {
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
      
      // Decode numeric entities (&#123; and &#x1F;)
      decoded = decoded.replace(/&#(\d+);/g, (match, dec) => String.fromCharCode(parseInt(dec, 10)));
      decoded = decoded.replace(/&#x([a-f\d]+);/gi, (match, hex) => String.fromCharCode(parseInt(hex, 16)));
      
      return decoded;
    } else {
      // Client-side: use DOM API for complete decoding
      const textarea = document.createElement('textarea');
      textarea.innerHTML = text;
      return textarea.value;
    }
  };

  // Extract URL and HTML content from Confluence articles
  const extractConfluenceData = (rawText: string): { url: string; html: string } => {
    if (!rawText) return { url: '', html: '' };
    
    // Check if it starts with "URL:" (Confluence format)
    if (rawText.startsWith('URL:')) {
      // Extract URL and HTML content
      const lines = rawText.split('\n');
      const urlLine = lines[0];
      const url = urlLine.replace(/^URL:\s*/, '').trim();
      const htmlContent = lines.slice(1).join('\n').trim();
      return { url, html: htmlContent };
    }
    
    // If no URL prefix, assume entire raw_text is HTML
    return { url: '', html: rawText };
  };

  // Sanitize HTML (basic - remove script tags and dangerous attributes)
  const sanitizeHtml = (html: string): string => {
    // Remove script tags and their content
    html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    // Remove event handlers
    html = html.replace(/on\w+="[^"]*"/gi, '');
    html = html.replace(/on\w+='[^']*'/gi, '');
    return html;
  };

  const messages = parseMessages(article?.raw_text || '');
  const isConfluence = article?.source === 'confluence';
  const confluenceData = isConfluence ? extractConfluenceData(article?.raw_text || '') : { url: '', html: '' };
  
  // Debug logging (remove in production)
  if (isConfluence) {
    console.log('Confluence article detected:', {
      hasHtml: !!confluenceData.html,
      htmlLength: confluenceData.html?.length,
      url: confluenceData.url
    });
  }

  return (
    <>
      <MainMenu />
      <Container>
        <BackButton href="/app/dashboard">← Back to Dashboard</BackButton>
      
      <Header>
        <Title>{getPageTitle()}</Title>
        <ButtonGroup>
          <Button href="/app/dashboard">🏠 Dashboard</Button>
          <Button href="/app/items">📖 All Articles</Button>
        </ButtonGroup>
      </Header>

      <ArticleCard>
        {isConfluence && confluenceData.html ? (
          <>
            {confluenceData.url && (
              <div style={{ marginBottom: '16px', padding: '12px', background: '#f4f5f7', borderRadius: '6px' }}>
                <a 
                  href={confluenceData.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ 
                    color: '#0052cc', 
                    textDecoration: 'none',
                    fontWeight: 500,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  🔗 View on Confluence
                </a>
              </div>
            )}
            <ConfluenceContent 
              dangerouslySetInnerHTML={{ 
                __html: sanitizeHtml(decodeHtmlEntities(confluenceData.html)) 
              }} 
            />
          </>
        ) : messages.length > 0 ? (
          messages.map((msg, index) => (
            <Section key={index}>
              <SectionTitle>
                💬 {msg.sender} <span style={{ color: '#6B7280', fontSize: '14px', fontWeight: 'normal' }}>• {msg.date}</span>
              </SectionTitle>
              <ArticleContent>{msg.text}</ArticleContent>
              
              {msg.attachments.length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <SectionTitle style={{ fontSize: '14px', marginBottom: '8px' }}>Attachments</SectionTitle>
                  <List>
                    {msg.attachments.map((att, attIndex) => (
                      <ListItem key={attIndex}>
                        <a 
                          href={att.url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          style={{ color: '#1D74F5', textDecoration: 'none' }}
                        >
                          📎 {att.name}
                        </a>
                      </ListItem>
                    ))}
                  </List>
                </div>
              )}
              {index < messages.length - 1 && <hr style={{ border: 'none', borderTop: '1px solid #e5e7eb', margin: '24px 0' }} />}
            </Section>
          ))
        ) : (
          <ArticleContent>{article.summary}</ArticleContent>
        )}

        <Metadata>
          <MetadataItem>
            <MetadataLabel>Project</MetadataLabel>
            <MetadataValue>{article.project || 'General'}</MetadataValue>
          </MetadataItem>
          {article.sender_name && (
            <MetadataItem>
              <MetadataLabel>Sender</MetadataLabel>
              <MetadataValue>{article.sender_name}</MetadataValue>
            </MetadataItem>
          )}
          <MetadataItem>
            <MetadataLabel>Source</MetadataLabel>
            <MetadataValue>{article.source || 'Unknown'}</MetadataValue>
          </MetadataItem>
          <MetadataItem>
            <MetadataLabel>Date</MetadataLabel>
            <MetadataValue>{new Date(article.created_at).toLocaleDateString()}</MetadataValue>
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