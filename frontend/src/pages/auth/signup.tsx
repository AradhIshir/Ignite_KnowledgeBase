import { useState } from 'react';
import { useForm } from 'react-hook-form';
import styled from 'styled-components';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { supabase } from '../../lib/supabaseClient';
import Link from 'next/link';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string().min(6, 'Password must be at least 6 characters'),
  fullName: z.string().min(2, 'Full name must be at least 2 characters')
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type FormValues = z.infer<typeof schema>;

const Wrapper = styled.div` display: flex; align-items: center; justify-content: center; height: 100%; padding: 24px; `;
const Card = styled.div`
  background: ${(p) => p.theme.colors.cardBg}; backdrop-filter: blur(8px); border: 1px solid ${(p) => p.theme.colors.border}; border-radius: ${(p) => p.theme.radii.xl}; box-shadow: ${(p) => p.theme.shadows.md}; padding: 32px; width: 100%; max-width: 520px;
`;
const Title = styled.h2` margin: 0 0 16px; color: ${(p) => p.theme.colors.secondary}; `;
const Field = styled.div` display: grid; gap: 8px; margin-bottom: 16px; `;
const Input = styled.input`
  padding: 12px 14px; border-radius: ${(p) => p.theme.radii.md}; border: 1px solid ${(p) => p.theme.colors.border}; background: ${(p) => p.theme.colors.surface}; color: ${(p) => p.theme.colors.text};
`;
const Button = styled.button` width: 100%; padding: 12px 16px; border-radius: ${(p) => p.theme.radii.lg}; background: ${(p) => p.theme.colors.secondary}; color: white; border: none; cursor: pointer; `;
const Hint = styled.div` font-size: 14px; color: ${(p) => p.theme.colors.muted}; `;
const ErrorMsg = styled.div` color: #D92D20; font-size: 14px; margin-bottom: 8px; `;
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

export default function SignUp() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const onSubmit = async (data: FormValues) => {
    setSubmitting(true); setError(null); setInfo(null);
    const { error } = await supabase.auth.signUp({
      email: data.email,
      password: data.password,
      options: { data: { full_name: data.fullName } }
    });
    setSubmitting(false);
    if (error) { setError(error.message); return; }
    setInfo('Your account is created successfully, confirm in the email.');
  };

  return (
    <Wrapper>
      <Card>
        <Title>Create your account</Title>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Field>
            <label>Full name</label>
            <Input placeholder="Alex Doe" {...register('fullName')} />
            {errors.fullName && <ErrorMsg>{errors.fullName.message}</ErrorMsg>}
          </Field>
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
          <Field>
            <label>Confirm Password</label>
            <Input placeholder="••••••••" type="password" {...register('confirmPassword')} />
            {errors.confirmPassword && <ErrorMsg>{errors.confirmPassword.message}</ErrorMsg>}
          </Field>
          {error && <ErrorMsg>{error}</ErrorMsg>}
          {info && <SuccessMsg>{info}</SuccessMsg>}
          <Button disabled={submitting}>{submitting ? 'Creating…' : 'Create account'}</Button>
        </form>
        <Hint style={{ marginTop: 12 }}>
          Already have an account? <StyledLink href="/auth/signin">Sign in</StyledLink>
        </Hint>
      </Card>
    </Wrapper>
  );
}

