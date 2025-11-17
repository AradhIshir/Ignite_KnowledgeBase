import { useState, useEffect } from 'react';
import styled from 'styled-components';
import { supabase } from '../lib/supabaseClient';
import { canAddComments, getUserRole } from '../lib/roles';

const CommentsContainer = styled.div`
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
`;

const CommentsTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
`;

const CommentList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
`;

const CommentItem = styled.div`
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #1D74F5;
`;

const CommentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const CommentAuthor = styled.span`
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
`;

const CommentDate = styled.span`
  color: #6b7280;
  font-size: 0.75rem;
`;

const CommentText = styled.p`
  color: #374151;
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
`;

const CommentForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const CommentTextarea = styled.textarea`
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: inherit;
  resize: vertical;
  min-height: 100px;
  
  &:focus {
    outline: none;
    border-color: #1D74F5;
    box-shadow: 0 0 0 3px rgba(29, 116, 245, 0.1);
  }
`;

const SubmitButton = styled.button`
  padding: 10px 20px;
  background: #1D74F5;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  align-self: flex-start;
  
  &:hover {
    background: #1565D8;
  }
  
  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

const NoComments = styled.p`
  color: #6b7280;
  font-style: italic;
  margin: 16px 0;
`;

const ErrorMessage = styled.div`
  background: #FEF2F2;
  border: 1px solid #FECACA;
  border-radius: 8px;
  padding: 12px 16px;
  color: #DC2626;
  font-size: 0.875rem;
  margin-bottom: 16px;
`;

interface Comment {
  id: string;
  comment_text: string;
  created_at: string;
  user_id: string;
  user_email?: string;
  user_name?: string;
}

interface CommentsProps {
  articleId: string;
}

export default function Comments({ articleId }: CommentsProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [canComment, setCanComment] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkPermissions();
    fetchComments();
  }, [articleId]);

  const checkPermissions = async () => {
    const hasPermission = await canAddComments();
    setCanComment(hasPermission);
  };

  const fetchComments = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('article_comments')
        .select(`
          id,
          comment_text,
          created_at,
          user_id
        `)
        .eq('article_id', articleId)
        .order('created_at', { ascending: false });

      if (error) throw error;

      // Fetch user info for each comment
      const commentsWithUsers = await Promise.all(
        (data || []).map(async (comment: any) => {
          try {
            // Get user info from auth.users (limited - we can only get current user)
            // For other users, we'll need to store name in a separate table or use backend
            const { data: { user: currentUser } } = await supabase.auth.getUser();
            let userName = 'Unknown';
            let userEmail = 'Unknown';

            if (comment.user_id === currentUser?.id) {
              userName = currentUser.user_metadata?.full_name || currentUser.email?.split('@')[0] || 'You';
              userEmail = currentUser.email || 'Unknown';
            } else {
              // For other users, try to get from a users table or use user_id
              // For now, we'll show a generic name
              userName = `User ${comment.user_id.substring(0, 8)}`;
            }

            return {
              id: comment.id,
              comment_text: comment.comment_text,
              created_at: comment.created_at,
              user_id: comment.user_id,
              user_email: userEmail,
              user_name: userName,
            };
          } catch (err) {
            return {
              id: comment.id,
              comment_text: comment.comment_text,
              created_at: comment.created_at,
              user_id: comment.user_id,
              user_email: 'Unknown',
              user_name: 'Unknown User',
            };
          }
        })
      );

      setComments(commentsWithUsers);
    } catch (err: any) {
      console.error('Error fetching comments:', err);
      let errorMessage = 'Failed to load comments. Please try again.';
      
      if (err.message) {
        errorMessage = err.message;
      } else if (err.error) {
        errorMessage = err.error;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      // Provide more specific error messages
      if (errorMessage.includes('permission') || errorMessage.includes('policy')) {
        errorMessage = 'You do not have permission to view comments.';
      } else if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
        errorMessage = 'Network error. Please check your internet connection and try again.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || !canComment) return;

    try {
      setSubmitting(true);
      setError(null);

      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        throw new Error('You must be logged in to comment');
      }

      const { error } = await supabase
        .from('article_comments')
        .insert({
          article_id: articleId,
          user_id: user.id,
          comment_text: newComment.trim(),
        });

      if (error) throw error;

      setNewComment('');
      await fetchComments();
    } catch (err: any) {
      console.error('Error submitting comment:', err);
      let errorMessage = 'Failed to add comment. Please try again.';
      
      if (err.message) {
        errorMessage = err.message;
      } else if (err.error) {
        errorMessage = err.error;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      // Provide more specific error messages
      if (errorMessage.includes('permission') || errorMessage.includes('role') || errorMessage.includes('policy')) {
        errorMessage = 'You do not have permission to add comments. Only Admins and Project Leads can comment.';
      } else if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
        errorMessage = 'Network error. Please check your internet connection and try again.';
      } else if (errorMessage.includes('authentication') || errorMessage.includes('login')) {
        errorMessage = 'You must be logged in to add comments. Please log in and try again.';
      }
      
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <CommentsContainer>
        <CommentsTitle>Comments</CommentsTitle>
        <p>Loading comments...</p>
      </CommentsContainer>
    );
  }

  return (
    <CommentsContainer>
      <CommentsTitle>Comments ({comments.length})</CommentsTitle>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}

      {comments.length === 0 ? (
        <NoComments>No comments yet. Be the first to comment!</NoComments>
      ) : (
        <CommentList>
          {comments.map((comment) => (
            <CommentItem key={comment.id}>
              <CommentHeader>
                <CommentAuthor>{comment.user_name}</CommentAuthor>
                <CommentDate>
                  {new Date(comment.created_at).toLocaleDateString()} at{' '}
                  {new Date(comment.created_at).toLocaleTimeString()}
                </CommentDate>
              </CommentHeader>
              <CommentText>{comment.comment_text}</CommentText>
            </CommentItem>
          ))}
        </CommentList>
      )}

      {canComment ? (
        <CommentForm onSubmit={handleSubmit}>
          <CommentTextarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment..."
            required
          />
          <SubmitButton type="submit" disabled={submitting || !newComment.trim()}>
            {submitting ? 'Posting...' : 'Post Comment'}
          </SubmitButton>
        </CommentForm>
      ) : (
        <p style={{ color: '#6b7280', fontStyle: 'italic' }}>
          Only Project Leads and Admins can add comments.
        </p>
      )}
    </CommentsContainer>
  );
}

