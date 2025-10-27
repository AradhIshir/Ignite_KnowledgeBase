import { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { upsertKnowledge } from '../../lib/api';
import { supabase } from '../../lib/supabaseClient';

const schema = z.object({
  summary: z.string().min(4),
  topics: z.string().optional(),
  decisions: z.string().optional(),
  faqs: z.string().optional(),
  source: z.string().optional(),
  date: z.string().optional(),
  project: z.string().optional(),
  raw_text: z.string().optional()
});
type FormValues = z.infer<typeof schema>;

const Shell = styled.div` padding: 24px; max-width: 900px; margin: 0 auto; `;
const Field = styled.div` display: grid; gap: 6px; margin-bottom: 12px; `;
const Input = styled.input` padding: 10px 12px; border: 1px solid ${(p) => p.theme.colors.border}; border-radius: ${(p) => p.theme.radii.md}; background: ${(p) => p.theme.colors.surface}; color: ${(p) => p.theme.colors.text}; `;
const Textarea = styled.textarea` padding: 10px 12px; min-height: 120px; border: 1px solid ${(p) => p.theme.colors.border}; border-radius: ${(p) => p.theme.radii.md}; background: ${(p) => p.theme.colors.surface}; color: ${(p) => p.theme.colors.text}; `;
const Button = styled.button` padding: 12px 16px; border-radius: ${(p) => p.theme.radii.lg}; background: ${(p) => p.theme.colors.secondary}; color: white; border: none; cursor: pointer; `;
const ErrorMsg = styled.div` color: #D92D20; font-size: 14px; `;

export default function Admin() {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const [info, setInfo] = useState<string | null>(null);
  const [allowed, setAllowed] = useState<boolean>(false);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      const role = (data.user?.user_metadata as any)?.role;
      setAllowed(role === 'admin');
    });
  }, []);

  const onSubmit = async (values: FormValues) => {
    const payload = {
      summary: values.summary,
      topics: values.topics ? values.topics.split(',').map(s => s.trim()).filter(Boolean) : null,
      decisions: values.decisions ? values.decisions.split('\n').filter(Boolean) : null,
      faqs: values.faqs ? values.faqs.split('\n').filter(Boolean) : null,
      source: values.source || null,
      date: values.date || null,
      project: values.project || null,
      raw_text: values.raw_text || null
    };
    await upsertKnowledge(payload);
    setInfo('Saved');
    reset();
  };

  if (!allowed) return <Shell>Admins only.</Shell>;

  return (
    <Shell>
      <h2 style={{ color: '#22C7A9' }}>Add knowledge item</h2>
      <form onSubmit={handleSubmit(onSubmit)}>
        <Field><label>Summary</label><Input {...register('summary')} />{errors.summary && <ErrorMsg>{errors.summary.message}</ErrorMsg>}</Field>
        <Field><label>Topics (comma separated)</label><Input {...register('topics')} /></Field>
        <Field><label>Decisions (one per line)</label><Textarea {...register('decisions')} /></Field>
        <Field><label>FAQs (one per line)</label><Textarea {...register('faqs')} /></Field>
        <Field><label>Source</label><Input {...register('source')} /></Field>
        <Field><label>Date</label><Input {...register('date')} /></Field>
        <Field><label>Project</label><Input {...register('project')} /></Field>
        <Field><label>Original content</label><Textarea {...register('raw_text')} /></Field>
        <Button type="submit">Save</Button>
        {info && <div style={{ marginTop: 8, color: '#1D74F5' }}>{info}</div>}
      </form>
    </Shell>
  );
}

