import { useState } from 'react';
import { useForm } from 'react-hook-form';
import styled from 'styled-components';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { supabase } from '../../lib/supabaseClient';
import Link from 'next/link';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6)
});

type FormValues = z.infer<typeof schema>;

const Wrapper = styled.div`
  display: flex; align-items: center; justify-content: center; height: 100%; padding: 24px;
`;
const Card = styled.div`
  background: ${(p) => p.theme.colors.cardBg};
  backdrop-filter: blur(8px);
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: ${(p) => p.theme.radii.xl};
  box-shadow: ${(p) => p.theme.shadows.md};
  padding: 32px; width: 100%; max-width: 480px;
`;
const Title = styled.h2` margin: 0 0 16px; color: ${(p) => p.theme.colors.primary}; `;
const Field = styled.div` display: grid; gap: 8px; margin-bottom: 16px; `;
const Input = styled.input`
  padding: 12px 14px; border-radius: ${(p) => p.theme.radii.md}; border: 1px solid ${(p) => p.theme.colors.border}; background: ${(p) => p.theme.colors.surface}; color: ${(p) => p.theme.colors.text};
`;
const Button = styled.button`
  width: 100%; padding: 12px 16px; border-radius: ${(p) => p.theme.radii.lg}; background: ${(p) => p.theme.colors.primary}; color: white; border: none; cursor: pointer;
`;
const Hint = styled.div` font-size: 14px; color: ${(p) => p.theme.colors.muted}; `;
const ErrorMsg = styled.div` color: #D92D20; font-size: 14px; `;
const StyledLink = styled(Link)`
  color: #1D74F5;
  text-decoration: none;
  font-weight: 500;
  &:hover {
    text-decoration: underline;
  }
`;
const LinkButton = styled.button`
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

export default function SignIn() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (data: FormValues) => {
    setSubmitting(true); setError(null);
    const { error } = await supabase.auth.signInWithPassword({ 
      email: data.email, 
      password: data.password 
    });
    setSubmitting(false);
    if (error) {
      setError(error.message);
      return;
    }
    // Sign in successful - redirect to dashboard
    window.location.href = '/app/dashboard';
  };

  return (
    <Wrapper>
      <Card>
        <Title>Welcome back</Title>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Field>
            <label>Email</label>
            <Input placeholder="you@company.com" type="email" {...register('email')} />
            {errors.email && <ErrorMsg>{errors.email.message}</ErrorMsg>}
          </Field>
          <Field>
            <label>Password</label>
            <Input placeholder="••••••••" type="password" {...register('password')} />
            {errors.password && <ErrorMsg>{errors.password.message}</ErrorMsg>}
          </Field>
          {error && <ErrorMsg>{error}</ErrorMsg>}
          <LinkButton disabled={submitting} type="submit">{submitting ? 'Signing in…' : 'Sign in'}</LinkButton>
        </form>
        <Hint style={{ marginTop: 12 }}>
          <StyledLink href="/auth/forgot">Forgot password?</StyledLink>
        </Hint>
        <Hint style={{ marginTop: 8 }}>
          No account? <StyledLink href="/auth/signup">Create one</StyledLink>
        </Hint>
      </Card>
    </Wrapper>
  );
}

