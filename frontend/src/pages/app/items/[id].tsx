import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import styled from 'styled-components';
import { supabase } from '../../../lib/supabaseClient';
import Link from 'next/link';
import MainMenu from '../../../components/MainMenu';
import Comments from '../../../components/Comments';

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
  word-wrap: break-word;
  
  /* Reset and base styles */
  * {
    box-sizing: border-box;
  }
  
  /* Confluence-like styling */
  h1, h2, h3, h4, h5, h6 {
    color: #172b4d;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 12px;
    line-height: 1.3;
  }
  
  h1 { font-size: 28px; }
  h2 { font-size: 24px; }
  h3 { font-size: 20px; }
  h4 { font-size: 18px; }
  h5 { font-size: 16px; }
  h6 { font-size: 15px; }
  
  h1:first-child, h2:first-child, h3:first-child {
    margin-top: 0;
  }
  
  p {
    margin: 12px 0;
    color: #172b4d;
    line-height: 1.6;
  }
  
  p:first-child {
    margin-top: 0;
  }
  
  p:last-child {
    margin-bottom: 0;
  }
  
  ul, ol {
    margin: 12px 0;
    padding-left: 24px;
  }
  
  ul:first-child, ol:first-child {
    margin-top: 0;
  }
  
  ul:last-child, ol:last-child {
    margin-bottom: 0;
  }
  
  li {
    margin: 6px 0;
    color: #172b4d;
    line-height: 1.6;
    list-style-position: outside;
  }
  
  /* Task list items */
  li[data-type="taskItem"],
  .task-list-item,
  li.task-item {
    list-style: none;
    padding-left: 8px;
    margin: 8px 0;
    position: relative;
    display: flex;
    align-items: flex-start;
  }
  
  li.task-item input[type="checkbox"] {
    margin-top: 4px;
    margin-right: 8px;
    flex-shrink: 0;
    cursor: default;
  }
  
  ul.confluence-task-list {
    list-style: none;
    padding-left: 0;
    margin: 16px 0;
  }
  
  .confluence-panel {
    padding: 16px;
    margin: 16px 0;
    border-radius: 4px;
    background: #f4f5f7;
    border-left: 4px solid #0052cc;
  }
  
  strong, b {
    font-weight: 600;
    color: #172b4d;
  }
  
  em, i {
    font-style: italic;
  }
  
  code {
    background: #f4f5f7;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Courier New', monospace;
    font-size: 13px;
    color: #e83e8c;
  }
  
  pre {
    background: #f4f5f7;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    margin: 12px 0;
    border: 1px solid #dfe1e6;
  }
  
  pre code {
    background: transparent;
    padding: 0;
    color: inherit;
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
    font-style: italic;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    border: 1px solid #dfe1e6;
  }
  
  th, td {
    border: 1px solid #dfe1e6;
    padding: 8px 12px;
    text-align: left;
    vertical-align: top;
  }
  
  th {
    background: #f4f5f7;
    font-weight: 600;
    color: #172b4d;
  }
  
  tr:nth-child(even) {
    background: #fafbfc;
  }
  
  /* Confluence-specific elements */
  .panel,
  .info-panel,
  .note-panel,
  .warning-panel,
  .tip-panel {
    padding: 12px 16px;
    margin: 12px 0;
    border-radius: 4px;
    border-left: 4px solid #0052cc;
    background: #f4f5f7;
  }
  
  /* Remove any inline styles that might interfere */
  [style*="display: none"] {
    display: none !important;
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

const SummarySection = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border-left: 4px solid #1D74F5;
`;

const SummaryTitle = styled.h2`
  font-size: 20px;
  font-weight: 700;
  color: #1D74F5;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SummaryContent = styled.div`
  color: #374151;
  font-size: 15px;
  line-height: 1.6;
  
  h2 {
    font-size: 18px;
    font-weight: 600;
    color: #1D74F5;
    margin-top: 16px;
    margin-bottom: 8px;
    
    &:first-child {
      margin-top: 0;
    }
  }
  
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #374151;
    margin-top: 12px;
    margin-bottom: 6px;
  }
  
  p {
    margin: 4px 0;
    color: #4b5563;
    line-height: 1.6;
    
    &:empty {
      display: none;
    }
  }
  
  ul, ol {
    margin: 4px 0 8px 0;
    padding-left: 24px;
  }
  
  li {
    margin: 4px 0;
    color: #4b5563;
    line-height: 1.5;
  }
  
  strong {
    font-weight: 600;
    color: #374151;
  }
`;

const Divider = styled.hr`
  border: none;
  border-top: 2px solid #e5e7eb;
  margin: 32px 0;
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
      setLoading(true);
      setError('');
      
      if (!id) {
        throw new Error('Article ID is missing');
      }

      const { data, error } = await supabase
        .from('knowledge_items')
        .select('*')
        .eq('id', id)
        .single();

      if (error) {
        if (error.code === 'PGRST116') {
          throw new Error('Article not found. It may have been deleted or you may not have permission to view it.');
        }
        throw error;
      }

      if (!data) {
        throw new Error('Article not found');
      }

      setArticle(data);
    } catch (err: any) {
      console.error('Error fetching article:', err);
      let errorMessage = 'Failed to load article. Please try again.';
      
      if (err.message) {
        errorMessage = err.message;
      } else if (err.error) {
        errorMessage = err.error;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      // Provide more specific error messages
      if (errorMessage.includes('not found') || errorMessage.includes('PGRST116')) {
        errorMessage = 'Article not found. It may have been deleted or you may not have permission to view it.';
      } else if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
        errorMessage = 'Network error. Please check your internet connection and try again.';
      } else if (errorMessage.includes('permission') || errorMessage.includes('policy')) {
        errorMessage = 'You do not have permission to view this article.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Parse grouped messages from raw_text
  const parseMessages = (rawText: string) => {
    try {
      if (!rawText || typeof rawText !== 'string') return [];
      
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
    } catch (err) {
      console.error('Error parsing messages:', err);
      // Return empty array if parsing fails
      return [];
    }
  };

  // Get page title: "Keyword" for Slack, actual title for Confluence
  const getPageTitle = () => {
    // For Confluence articles, use the actual page title
    if (isConfluence) {
      return getConfluenceTitle();
    }
    
    // For Slack articles, use keyword from topics
    if (article?.topics && article.topics.length > 0) {
      // Capitalize first letter of each word in keyword
      const keyword = article.topics[0];
      const keywordTitle = keyword.split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
      ).join(' ');
      return keywordTitle;
    }
    
    // Fallback
    return article?.summary || 'Article Details';
  };

  if (loading) {
    return (
      <>
        <MainMenu />
        <Container>
          <BackButton href="/app/dashboard">← Back to Dashboard</BackButton>
          <LoadingState>Loading article...</LoadingState>
        </Container>
      </>
    );
  }

  if (error || !article) {
    return (
      <>
        <MainMenu />
        <Container>
          <BackButton href="/app/dashboard">← Back to Dashboard</BackButton>
          <ErrorState>
            <h2>Article not found</h2>
            <p>{error || 'The article you are looking for does not exist.'}</p>
            <ButtonGroup style={{ marginTop: '24px' }}>
              <Button href="/app/dashboard">← Back to Dashboard</Button>
              <Button href="/app/items">View All Articles</Button>
            </ButtonGroup>
          </ErrorState>
        </Container>
      </>
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

  // Extract URL, title, and HTML content from Confluence articles
  const extractConfluenceData = (rawText: string): { url: string; title: string; html: string } => {
    if (!rawText) return { url: '', title: '', html: '' };
    
    let url = '';
    let title = '';
    let htmlContent = '';
    const lines = rawText.split('\n');
    let contentStartIndex = 0;
    
    // Extract metadata from header (URL, CONFLUENCE_PAGE_TITLE, CONFLUENCE_PAGE_ID, CONFLUENCE_VERSION, CONFLUENCE_VERSION_DATE)
    for (let i = 0; i < Math.min(lines.length, 15); i++) {
      const line = lines[i].trim();
      
      if (line.startsWith('URL:')) {
        url = line.replace(/^URL:\s*/, '').trim();
        contentStartIndex = Math.max(contentStartIndex, i + 1);
      } else if (line.startsWith('CONFLUENCE_PAGE_TITLE:')) {
        title = line.replace(/^CONFLUENCE_PAGE_TITLE:\s*/, '').trim();
        // Decode URL-encoded characters in title (e.g., + becomes space)
        try {
          title = decodeURIComponent(title.replace(/\+/g, '%20'));
        } catch (e) {
          // If decoding fails, just replace + with space
          title = title.replace(/\+/g, ' ');
        }
        contentStartIndex = Math.max(contentStartIndex, i + 1);
      } else if (line.startsWith('CONFLUENCE_PAGE_ID:') || 
                 line.startsWith('CONFLUENCE_VERSION:') || 
                 line.startsWith('CONFLUENCE_VERSION_DATE:')) {
        // Skip metadata lines - don't include in content
        contentStartIndex = Math.max(contentStartIndex, i + 1);
      } else if (line === '' && contentStartIndex <= i) {
        // Skip empty lines in the header section
        contentStartIndex = i + 1;
      } else if (line && !line.startsWith('URL:') && 
                 !line.startsWith('CONFLUENCE_PAGE_TITLE:') &&
                 !line.startsWith('CONFLUENCE_PAGE_ID:') && 
                 !line.startsWith('CONFLUENCE_VERSION:') && 
                 !line.startsWith('CONFLUENCE_VERSION_DATE:')) {
        // Found actual content, stop processing header
        break;
      }
    }
    
    // Get HTML content (everything after the metadata header)
    htmlContent = lines.slice(contentStartIndex).join('\n').trim();
    
    // Additional cleanup: remove any remaining metadata lines that might be in the content
    htmlContent = htmlContent.replace(/^(URL|CONFLUENCE_PAGE_TITLE|CONFLUENCE_PAGE_ID|CONFLUENCE_VERSION|CONFLUENCE_VERSION_DATE):\s*.*$/gim, '');
    htmlContent = htmlContent.trim();
    
    // If no URL was found but content exists, try to extract from first line
    if (!url && rawText.startsWith('URL:')) {
      const urlLine = lines[0];
      url = urlLine.replace(/^URL:\s*/, '').trim();
    }
    
    return { url, title, html: htmlContent };
  };

  // Convert Confluence XML format to standard HTML
  const convertConfluenceToHtml = (html: string): string => {
    if (!html) return '';
    
    // Convert Confluence task lists to HTML lists
    // Replace <ac:task-list> with <ul>
    html = html.replace(/<ac:task-list[^>]*>/gi, '<ul class="confluence-task-list">');
    html = html.replace(/<\/ac:task-list>/gi, '</ul>');
    
    // Replace <ac:task> with <li> and remove task metadata
    // Pattern: <ac:task>...<ac:task-id>...</ac:task-id><ac:task-uuid>...</ac:task-uuid><ac:task-status>...</ac:task-status><ac:task-body>...</ac:task-body></ac:task>
    html = html.replace(/<ac:task[^>]*>[\s\S]*?<ac:task-id>(\d+)<\/ac:task-id>[\s\S]*?<ac:task-uuid>[^<]*<\/ac:task-uuid>[\s\S]*?<ac:task-status>([^<]*)<\/ac:task-status>[\s\S]*?<ac:task-body>([\s\S]*?)<\/ac:task-body>[\s\S]*?<\/ac:task>/gi, 
      (match, taskId, status, body) => {
        // Extract content from task body, removing placeholder spans
        let content = body.replace(/<span[^>]*class="placeholder-inline-tasks"[^>]*>/gi, '');
        content = content.replace(/<\/span>/gi, '');
        // Clean up any trailing dashes or extra spaces
        content = content.replace(/\s*-\s*$/, '').trim();
        // Return as list item with checkbox styling
        const checked = status === 'complete' ? 'checked' : '';
        return `<li class="task-item" data-task-id="${taskId}" data-status="${status}"><input type="checkbox" ${checked} disabled style="margin-right: 8px;">${content}</li>`;
      }
    );
    
    // Convert Confluence structured macros (panels, etc.) to divs
    html = html.replace(/<ac:structured-macro[^>]*ac:name="panel"[^>]*>[\s\S]*?<ac:rich-text-body>([\s\S]*?)<\/ac:rich-text-body>[\s\S]*?<\/ac:structured-macro>/gi, 
      '<div class="confluence-panel">$1</div>'
    );
    
    // Remove other Confluence-specific tags but keep their content
    html = html.replace(/<ac:[^>]*>/gi, '');
    html = html.replace(/<\/ac:[^>]*>/gi, '');
    
    // Clean up empty paragraphs
    html = html.replace(/<p\s*\/>/gi, '');
    html = html.replace(/<p>\s*<\/p>/gi, '');
    
    return html;
  };

  // Sanitize HTML (basic - remove script tags and dangerous attributes)
  const sanitizeHtml = (html: string): string => {
    if (!html) return '';
    
    // First, convert Confluence XML to standard HTML
    html = convertConfluenceToHtml(html);
    
    // Remove script tags and their content
    html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    // Remove event handlers
    html = html.replace(/on\w+="[^"]*"/gi, '');
    html = html.replace(/on\w+='[^']*'/gi, '');
    
    // Clean up extra whitespace but preserve line breaks in HTML
    html = html.replace(/>\s+</g, '><');
    html = html.replace(/\s{3,}/g, ' '); // Replace 3+ spaces with single space
    
    return html;
  };

  // Format summary markdown text for display
  const formatSummary = (summaryText: string): string => {
    try {
      if (!summaryText || typeof summaryText !== 'string') {
        return '';
      }
      
      // Decode HTML entities first
      let formatted = decodeHtmlEntities(summaryText);
      
      // Remove excessive blank lines (more than 2 consecutive newlines)
      formatted = formatted.replace(/\n{3,}/g, '\n\n');
      
      // Split into lines for processing
      const lines = formatted.split('\n');
      const result: string[] = [];
      let inList = false;
      let lastWasHeader = false;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Skip empty lines (but allow one after headers/lists for spacing)
        if (!line) {
          if (inList) {
            result.push('</ul>');
            inList = false;
            lastWasHeader = false;
          }
          // Only add spacing if last element wasn't a header
          if (!lastWasHeader && result.length > 0 && !result[result.length - 1].endsWith('</ul>')) {
            // Don't add extra spacing, just continue
          }
          continue;
        }
        
        // Check for headers
        if (line.startsWith('## ')) {
          if (inList) {
            result.push('</ul>');
            inList = false;
          }
          result.push(`<h2>${line.substring(3)}</h2>`);
          lastWasHeader = true;
          continue;
        }
        
        if (line.startsWith('### ')) {
          if (inList) {
            result.push('</ul>');
            inList = false;
          }
          result.push(`<h3>${line.substring(4)}</h3>`);
          lastWasHeader = true;
          continue;
        }
        
        // Check for numbered list items (1. item)
        const listMatch = line.match(/^(\d+)\.\s+(.+)$/);
        if (listMatch) {
          if (!inList) {
            result.push('<ul>');
            inList = true;
          }
          result.push(`<li>${listMatch[2]}</li>`);
          lastWasHeader = false;
          continue;
        }
        
        // Regular paragraph text
        if (inList) {
          result.push('</ul>');
          inList = false;
        }
        
        // Collect paragraph text (handle multi-line paragraphs)
        const paragraphLines: string[] = [line];
        let j = i + 1;
        
        // Collect consecutive non-empty lines that aren't headers or list items
        while (j < lines.length) {
          const nextLine = lines[j].trim();
          if (!nextLine) break;
          if (nextLine.startsWith('##') || nextLine.match(/^\d+\.\s+/)) break;
          paragraphLines.push(nextLine);
          j++;
        }
        
        // Update i to skip processed lines
        i = j - 1;
        
        // Join paragraph lines with space (not <br> to avoid excessive spacing)
        const paragraphText = paragraphLines.join(' ');
        if (paragraphText.trim()) {
          result.push(`<p>${paragraphText}</p>`);
        }
        lastWasHeader = false;
      }
      
      // Close any open list
      if (inList) {
        result.push('</ul>');
      }
      
      // Remove empty paragraphs and clean up
      return result
        .filter(html => html.trim() && !html.match(/^<p>\s*<\/p>$/))
        .join('');
    } catch (err) {
      console.error('Error formatting summary:', err);
      // Return the original text if formatting fails
      return summaryText || '';
    }
  };

  const messages = parseMessages(article?.raw_text || '');
  const isConfluence = article?.source === 'confluence';
  const confluenceData = isConfluence ? extractConfluenceData(article?.raw_text || '') : { url: '', title: '', html: '' };
  
  // Get Confluence page title from metadata or fallback to extracting from summary
  const getConfluenceTitle = (): string => {
    if (confluenceData.title) {
      return decodeHtmlEntities(confluenceData.title);
    }
    // Fallback: try to extract from URL
    if (confluenceData.url) {
      // Extract title from URL (last part of the path)
      const urlParts = confluenceData.url.split('/');
      const lastPart = urlParts[urlParts.length - 1];
      if (lastPart && lastPart !== 'pages') {
        // Decode URL-encoded characters (e.g., + becomes space, %20 becomes space)
        try {
          const decoded = decodeURIComponent(lastPart);
          // Replace + with space and clean up
          const cleaned = decoded.replace(/\+/g, ' ').replace(/-/g, ' ').trim();
          return decodeHtmlEntities(cleaned);
        } catch (e) {
          // If decoding fails, just replace + and - with spaces
          return decodeHtmlEntities(lastPart.replace(/\+/g, ' ').replace(/-/g, ' '));
        }
      }
    }
    // Last fallback: use summary if it's a simple title (not AI-generated)
    if (article?.summary && !article.summary.includes('## Summary')) {
      return decodeHtmlEntities(article.summary);
    }
    return 'Confluence Article';
  };
  
  // Format summary for display (works for both Slack and Confluence)
  const formatSummaryForDisplay = (summaryText: string, isConfluenceArticle: boolean): string => {
    if (!summaryText || typeof summaryText !== 'string') return '';
    
    // For Confluence, the summary is usually just the page title
    // If it's a simple title (no markdown), just return it as a paragraph
    if (isConfluenceArticle) {
      // Check if it's just plain text (no markdown headers)
      if (!summaryText.includes('##') && !summaryText.includes('###')) {
        return `<p>${decodeHtmlEntities(summaryText)}</p>`;
      }
    }
    
    // For Slack articles or Confluence with markdown, use the full formatter
    return formatSummary(summaryText);
  };
  
  // Check if we should show summary (for both Slack and Confluence articles)
  const shouldShowSummary = article?.summary && article.summary.trim().length > 0;
  const formattedSummary = shouldShowSummary ? formatSummaryForDisplay(article.summary, isConfluence) : '';
  
  // Check if we have key points or action items to display
  // For Confluence articles, if the summary already contains "Key Points", don't show them separately
  const summaryHasKeyPoints = isConfluence && formattedSummary && formattedSummary.includes('Key Points');
  const hasKeyPoints = !summaryHasKeyPoints && article?.key_points && Array.isArray(article.key_points) && article.key_points.length > 0;
  const hasActionItems = article?.action_items && Array.isArray(article.action_items) && article.action_items.length > 0;
  const hasSummaryContent = formattedSummary || hasKeyPoints || hasActionItems;
  
  // Debug logging (remove in production)
  if (isConfluence) {
    console.log('Confluence article detected:', {
      hasHtml: !!confluenceData.html,
      htmlLength: confluenceData.html?.length,
      url: confluenceData.url,
      hasSummary: !!article?.summary,
      hasKeyPoints,
      hasActionItems
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

      {/* Summary Section - Show at top for both Slack and Confluence articles */}
      {hasSummaryContent && (
        <>
          <SummarySection>
            <SummaryTitle>📋 Summary</SummaryTitle>
            {formattedSummary && (
              <SummaryContent 
                dangerouslySetInnerHTML={{ 
                  __html: sanitizeHtml(formattedSummary) 
                }} 
              />
            )}
            
            {/* Key Points Section */}
            {hasKeyPoints && (
              <div style={{ marginTop: formattedSummary ? '16px' : '0' }}>
                <h3 style={{ 
                  fontSize: '16px', 
                  fontWeight: 600, 
                  color: '#1D74F5', 
                  marginTop: '0',
                  marginBottom: '8px' 
                }}>
                  Key Points
                </h3>
                <ul style={{ 
                  margin: '4px 0 0 0', 
                  paddingLeft: '24px',
                  listStyle: 'disc'
                }}>
                  {article.key_points.map((point: string, index: number) => (
                    <li key={index} style={{ 
                      margin: '4px 0', 
                      color: '#4b5563', 
                      lineHeight: '1.6',
                      fontSize: '15px'
                    }}>
                      {decodeHtmlEntities(point)}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Action Items Section */}
            {hasActionItems && (
              <div style={{ marginTop: (formattedSummary || hasKeyPoints) ? '16px' : '0' }}>
                <h3 style={{ 
                  fontSize: '16px', 
                  fontWeight: 600, 
                  color: '#1D74F5', 
                  marginTop: '0',
                  marginBottom: '8px' 
                }}>
                  Action Items
                </h3>
                <ul style={{ 
                  margin: '4px 0 0 0', 
                  paddingLeft: '24px',
                  listStyle: 'disc'
                }}>
                  {article.action_items.map((item: string, index: number) => (
                    <li key={index} style={{ 
                      margin: '4px 0', 
                      color: '#4b5563', 
                      lineHeight: '1.6',
                      fontSize: '15px'
                    }}>
                      {decodeHtmlEntities(item)}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </SummarySection>
          <Divider />
        </>
      )}

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
                __html: sanitizeHtml(confluenceData.html) 
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

      {article && article.id && (
        <Comments articleId={article.id} />
      )}
    </Container>
    </>
  );
}