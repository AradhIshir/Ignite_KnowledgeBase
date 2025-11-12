import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import styled from 'styled-components';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { supabase } from '../../lib/supabaseClient';
import Link from 'next/link';
import { useRouter } from 'next/router';

const schema = z.object({
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string().min(6, 'Password must be at least 6 characters')
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type FormValues = z.infer<typeof schema>;

const Wrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 24px;
`;

const Card = styled.div`
  background: ${(p) => p.theme.colors.cardBg};
  backdrop-filter: blur(8px);
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: ${(p) => p.theme.radii.xl};
  box-shadow: ${(p) => p.theme.shadows.md};
  padding: 32px;
  width: 100%;
  max-width: 520px;
`;

const Title = styled.h2`
  margin: 0 0 16px;
  color: ${(p) => p.theme.colors.primary};
`;

const Field = styled.div`
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
`;

const Input = styled.input`
  padding: 12px 14px;
  border-radius: ${(p) => p.theme.radii.md};
  border: 1px solid ${(p) => p.theme.colors.border};
  background: ${(p) => p.theme.colors.surface};
  color: ${(p) => p.theme.colors.text};
`;

const Button = styled.button`
  width: 100%;
  padding: 12px 16px;
  border-radius: ${(p) => p.theme.radii.lg};
  background: #1D74F5;
  color: white;
  border: none;
  cursor: pointer;
  font-weight: 500;
  &:hover {
    background: #1565D8;
  }
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const Hint = styled.div`
  font-size: 14px;
  color: ${(p) => p.theme.colors.muted};
`;

const ErrorMsg = styled.div`
  color: #D92D20;
  font-size: 14px;
  margin-bottom: 8px;
`;

const SuccessMsg = styled.div`
  color: #059669;
  font-size: 14px;
  background: #D1FAE5;
  border: 1px solid #10B981;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  font-weight: 500;
`;

const StyledLink = styled(Link)`
  color: #1D74F5;
  text-decoration: none;
  font-weight: 500;
  &:hover {
    text-decoration: underline;
  }
`;

export default function UpdatePassword() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema)
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [linkError, setLinkError] = useState<string | null>(null);

  useEffect(() => {
    // Check for error in URL hash (from Supabase redirect)
    if (typeof window !== 'undefined') {
      const hash = window.location.hash;
      const params = new URLSearchParams(hash.substring(1));
      
      if (params.get('error')) {
        const errorDescription = params.get('error_description') || params.get('error');
        if (errorDescription) {
          setLinkError(decodeURIComponent(errorDescription.replace(/\+/g, ' ')));
        } else {
          setLinkError('The reset link is invalid or has expired. Please request a new one.');
        }
      } else {
        // Check if we have an access token in the hash
        const accessToken = params.get('access_token');
        if (!accessToken) {
          // Try to get session to see if user is already authenticated
          supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session) {
              setLinkError('No valid reset token found. Please request a new password reset link.');
            }
          });
        }
      }
    }
  }, []);

  const onSubmit = async (data: FormValues) => {
    setSubmitting(true);
    setError(null);

    try {
      // Update password
      const { error: updateError } = await supabase.auth.updateUser({
        password: data.password
      });

      setSubmitting(false);

      if (updateError) {
        setError(updateError.message);
        return;
      }

      setSuccess(true);
      
      // Redirect to sign in after 2 seconds
      setTimeout(() => {
        router.push('/auth/signin');
      }, 2000);
    } catch (err: any) {
      setSubmitting(false);
      setError(err.message || 'An error occurred while updating your password.');
    }
  };

  if (linkError) {
    return (
      <Wrapper>
        <Card>
          <Title>Reset Link Error</Title>
          <ErrorMsg>{linkError}</ErrorMsg>
          <Hint style={{ marginTop: 16 }}>
            <StyledLink href="/auth/forgot">Request a new reset link</StyledLink>
          </Hint>
          <Hint style={{ marginTop: 8 }}>
            <StyledLink href="/auth/signin">Back to sign in</StyledLink>
          </Hint>
        </Card>
      </Wrapper>
    );
  }

  if (success) {
    return (
      <Wrapper>
        <Card>
          <Title>Password Updated</Title>
          <SuccessMsg>Your password has been updated successfully. Redirecting to sign in...</SuccessMsg>
          <Hint style={{ marginTop: 16 }}>
            <StyledLink href="/auth/signin">Go to sign in</StyledLink>
          </Hint>
        </Card>
      </Wrapper>
    );
  }

  return (
    <Wrapper>
      <Card>
        <Title>Set new password</Title>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Field>
            <label>New Password</label>
            <Input
              placeholder="••••••••"
              type="password"
              {...register('password')}
            />
            {errors.password && <ErrorMsg>{errors.password.message}</ErrorMsg>}
          </Field>
          <Field>
            <label>Confirm New Password</label>
            <Input
              placeholder="••••••••"
              type="password"
              {...register('confirmPassword')}
            />
            {errors.confirmPassword && <ErrorMsg>{errors.confirmPassword.message}</ErrorMsg>}
          </Field>
          {error && <ErrorMsg>{error}</ErrorMsg>}
          <Button disabled={submitting} type="submit">
            {submitting ? 'Updating…' : 'Update password'}
          </Button>
        </form>
        <Hint style={{ marginTop: 12 }}>
          <StyledLink href="/auth/signin">Back to sign in</StyledLink>
        </Hint>
      </Card>
    </Wrapper>
  );
}

