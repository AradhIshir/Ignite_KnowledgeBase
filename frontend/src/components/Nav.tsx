import Link from 'next/link';
import styled from 'styled-components';
import { supabase } from '../lib/supabaseClient';
import { useEffect, useState } from 'react';

const Bar = styled.nav`
  position: sticky; top: 0; z-index: 10; backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 12px 16px; border-bottom: 1px solid #D7E2EE; background: rgba(255,255,255,0.85);
`;
const Brand = styled.div` font-weight: 700; color: #1D74F5; `;
const Row = styled.div` display: flex; gap: 12px; align-items: center; `;
const Btn = styled.button` padding: 8px 12px; border-radius: 10px; border: 1px solid #D7E2EE; background: #ffffff; color: #0F2A43; cursor: pointer; `;

export function Nav() {
  const [email, setEmail] = useState<string | null>(null);
  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setEmail(data.user?.email ?? null));
  }, []);
  return (
    <Bar>
      <Row>
        <Brand>Ignite</Brand>
        <Link href="/app/dashboard">Dashboard</Link>
        <Link href="/app/items">Knowledge</Link>
        <Link href="/app/admin">Admin</Link>
        <Link href="/help">Help</Link>
      </Row>
      <Row>
        <Link href="/app/profile">{email ?? 'Profile'}</Link>
        <Btn onClick={() => (window as any).themeToggle?.()}>Theme</Btn>
      </Row>
    </Bar>
  );
}

