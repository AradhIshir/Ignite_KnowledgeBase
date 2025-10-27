import { useEffect, useState } from 'react';
import styled from 'styled-components';
import { supabase } from '../../lib/supabaseClient';

const Shell = styled.div` padding: 24px; max-width: 720px; margin: 0 auto; `;
const Field = styled.div` display: grid; gap: 6px; margin-bottom: 12px; `;
const Input = styled.input` padding: 10px 12px; border: 1px solid ${(p) => p.theme.colors.border}; border-radius: ${(p) => p.theme.radii.md}; background: ${(p) => p.theme.colors.surface}; color: ${(p) => p.theme.colors.text}; `;
const Button = styled.button` padding: 12px 16px; border-radius: ${(p) => p.theme.radii.lg}; background: ${(p) => p.theme.colors.primary}; color: white; border: none; cursor: pointer; `;

export default function Profile() {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setEmail(data.user?.email ?? '');
      setFullName((data.user?.user_metadata as any)?.full_name ?? '');
    });
  }, []);

  const save = async () => {
    await supabase.auth.updateUser({ data: { full_name: fullName } });
    alert('Saved');
  };

  const changePassword = async () => {
    const newPass = prompt('New password');
    if (!newPass) return;
    const { error } = await supabase.auth.updateUser({ password: newPass });
    if (error) alert(error.message); else alert('Password updated');
  };

  return (
    <Shell>
      <h2 style={{ color: '#1D74F5' }}>Profile</h2>
      <Field><label>Email</label><Input value={email} disabled /></Field>
      <Field><label>Full name</label><Input value={fullName} onChange={(e) => setFullName(e.target.value)} /></Field>
      <div style={{ display: 'flex', gap: 8 }}>
        <Button onClick={save}>Save</Button>
        <Button onClick={changePassword} style={{ background: '#22C7A9' }}>Change password</Button>
      </div>
    </Shell>
  );
}

