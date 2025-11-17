import { useState } from 'react';
import { useRouter } from 'next/router';
import styled from 'styled-components';
import MainMenu from '../../components/MainMenu';
import { askAIQuestion } from '../../lib/api';
import Link from 'next/link';

const Container = styled.div`
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
`;

const Header = styled.div`
  margin-bottom: 32px;
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

const QuestionForm = styled.form`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const InputGroup = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
`;

const QuestionInput = styled.input`
  flex: 1;
  padding: 14px 16px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #1D74F5;
    box-shadow: 0 0 0 3px rgba(29, 116, 245, 0.1);
  }

  &::placeholder {
    color: #9ca3af;
  }
`;

const SubmitButton = styled.button<{ disabled?: boolean }>`
  padding: 14px 28px;
  background: ${props => props.disabled ? '#9ca3af' : '#1D74F5'};
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: background-color 0.2s;

  &:hover:not(:disabled) {
    background: #1d5bb8;
  }

  &:active:not(:disabled) {
    background: #1a4fa0;
  }
`;

const ExampleQuestions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const ExampleButton = styled.button`
  padding: 8px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
  }
`;

const ResponseCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const ResponseTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: #1D74F5;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AnswerText = styled.div`
  color: #374151;
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 24px;
  white-space: pre-wrap;
  
  a {
    color: #1D74F5;
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
  
  ul, ol {
    margin: 12px 0;
    padding-left: 24px;
  }
  
  li {
    margin: 6px 0;
  }
`;

const ArticlesSection = styled.div`
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
`;

const ArticlesTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 16px 0;
`;

const ArticleList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ArticleLink = styled(Link)`
  display: block;
  padding: 12px 16px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.2s;

  &:hover {
    background: #f3f4f6;
    border-color: #1D74F5;
    transform: translateX(4px);
  }
`;

const ArticleTitle = styled.div`
  font-weight: 600;
  color: #1D74F5;
  margin-bottom: 4px;
`;

const ArticleMeta = styled.div`
  font-size: 14px;
  color: #6B7280;
`;

const ErrorMessage = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  color: #dc2626;
  font-size: 14px;
  margin-bottom: 24px;
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

export default function AIAssistant() {
  const router = useRouter();
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [articleLinks, setArticleLinks] = useState<Array<{ id: string; title: string; url: string }>>([]);
  const [error, setError] = useState<string | null>(null);

  const exampleQuestions = [
    "What is the status of Dashboard?",
    "Tell me about UI issues",
    "What are the latest updates on Recommendations?",
    "Show me information about Mia Chatbot"
  ];

  // Parse markdown links and convert to HTML
  const parseMarkdownLinks = (text: string): string => {
    if (!text) return '';
    
    // Convert markdown links [text](url) to HTML links
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let html = text.replace(linkRegex, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Convert line breaks to <br> tags
    html = html.replace(/\n/g, '<br>');
    
    return html;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    setError(null);
    setAnswer(null);
    setArticleLinks([]);

    try {
      const response = await askAIQuestion(question.trim());
      setAnswer(response.answer);
      setArticleLinks(response.article_links || []);
    } catch (err: any) {
      setError(
        err.message || 
        'Failed to get AI response. Please try again or check if the backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = async (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
    setLoading(true);
    setError(null);
    setAnswer(null);
    setArticleLinks([]);

    try {
      const response = await askAIQuestion(exampleQuestion);
      setAnswer(response.answer);
      setArticleLinks(response.article_links || []);
    } catch (err: any) {
      setError(
        err.message || 
        'Failed to get AI response. Please try again or check if the backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <MainMenu />
      <Container>
        <Header>
          <Title>🤖 AI Assistant</Title>
          <Subtitle>Ask questions about your knowledge base and get instant AI-powered answers</Subtitle>
        </Header>

        <QuestionForm onSubmit={handleSubmit}>
          <InputGroup>
            <QuestionInput
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question, e.g., 'What is the status of Dashboard?'"
              disabled={loading}
            />
            <SubmitButton type="submit" disabled={loading || !question.trim()}>
              {loading ? <LoadingSpinner /> : 'Ask'}
            </SubmitButton>
          </InputGroup>
          
          <div>
            <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
              Try these examples:
            </div>
            <ExampleQuestions>
              {exampleQuestions.map((example, index) => (
                <ExampleButton
                  key={index}
                  type="button"
                  onClick={() => handleExampleClick(example)}
                  disabled={loading}
                >
                  {example}
                </ExampleButton>
              ))}
            </ExampleQuestions>
          </div>
        </QuestionForm>

        {error && (
          <ErrorMessage>
            <strong>Error:</strong> {error}
          </ErrorMessage>
        )}

        {answer && (
          <ResponseCard>
            <ResponseTitle>
              💡 AI Answer
            </ResponseTitle>
            <AnswerText dangerouslySetInnerHTML={{ __html: parseMarkdownLinks(answer) }} />
            
            {articleLinks.length > 0 && (
              <ArticlesSection>
                <ArticlesTitle>📚 Relevant Articles</ArticlesTitle>
                <ArticleList>
                  {articleLinks.map((article) => (
                    <ArticleLink key={article.id} href={article.url}>
                      <ArticleTitle>{article.title}</ArticleTitle>
                      <ArticleMeta>Click to view full article →</ArticleMeta>
                    </ArticleLink>
                  ))}
                </ArticleList>
              </ArticlesSection>
            )}
          </ResponseCard>
        )}
      </Container>
    </>
  );
}

