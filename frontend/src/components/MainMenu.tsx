import { useEffect, useState } from 'react';
import styled from 'styled-components';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { supabase } from '../lib/supabaseClient';
import { canCreateArticles, isAdmin, getUserRole } from '../lib/roles';

const MenuContainer = styled.div`
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  background: #1D74F5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
`;

const LogoText = styled.div`
  display: flex;
  flex-direction: column;
`;

const LogoTitle = styled.h1`
  font-size: 18px;
  font-weight: 700;
  color: #1D74F5;
  margin: 0;
`;

const LogoSubtitle = styled.p`
  font-size: 12px;
  color: #6B7280;
  margin: 0;
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 24px;
`;

const NavLink = styled(Link)<{ $active?: boolean }>`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.$active ? '#1D74F5' : '#374151'};
  text-decoration: none;
  font-weight: ${props => props.$active ? '600' : '500'};
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
  background: ${props => props.$active ? '#f0f7ff' : 'transparent'};

  &:hover {
    background-color: #f3f4f6;
  }
`;

const UserProfile = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const UserAvatar = styled.div`
  width: 32px;
  height: 32px;
  background: #1D74F5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
`;

const UserName = styled.span`
  font-size: 14px;
  color: #374151;
  font-weight: 500;
`;

const LogoutButton = styled.button`
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #f3f4f6;
    border-color: #9ca3af;
  }
  
  &:active {
    background: #e5e7eb;
  }
`;

export default function MainMenu() {
  const router = useRouter();
  const [userRole, setUserRole] = useState<string | null>(null);
  const [canCreate, setCanCreate] = useState(false);
  const [isAdminUser, setIsAdminUser] = useState(false);
  const [userName, setUserName] = useState('User');

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const role = await getUserRole();
        setUserRole(role);
        setCanCreate(await canCreateArticles());
        setIsAdminUser(await isAdmin());
        setUserName(user.user_metadata?.full_name || user.email?.split('@')[0] || 'User');
      }
    } catch (error) {
      console.error('Error loading user info:', error);
    }
  };

  const isActive = (path: string) => {
    if (path === '/app/dashboard') {
      return router.pathname === '/app/dashboard';
    }
    if (path === '/app/items') {
      return router.pathname.startsWith('/app/items');
    }
    if (path === '/app/ai-assistant') {
      return router.pathname === '/app/ai-assistant';
    }
    return router.pathname === path;
  };

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      router.push('/auth/signin');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <MenuContainer>
      <Logo>
        <LogoIcon>📚</LogoIcon>
        <LogoText>
          <LogoTitle>KnowledgeHub</LogoTitle>
          <LogoSubtitle>Team Knowledge Base</LogoSubtitle>
        </LogoText>
      </Logo>
      
      <Nav>
        <NavLink href="/app/dashboard" $active={isActive('/app/dashboard')}>
          🏠 Home
        </NavLink>
        <NavLink href="/app/ai-assistant" $active={router.pathname === '/app/ai-assistant'}>
          🤖 AI Assistant
        </NavLink>
        {/* PAUSED: Knowledge Items tab - commented out for manual control
        <NavLink href="/app/items" $active={isActive('/app/items')}>
          📖 Knowledge Items
        </NavLink>
        */}
        {canCreate && (
          <NavLink href="/app/items/new" $active={false}>
            ➕ Add Article
          </NavLink>
        )}
        {isAdminUser && (
          <NavLink href="/app/admin" $active={router.pathname === '/app/admin'}>
            ⚙️ Admin
          </NavLink>
        )}
      </Nav>

      <UserProfile>
        <UserAvatar>{userName.charAt(0).toUpperCase()}</UserAvatar>
        <UserName>{userName}</UserName>
        <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
      </UserProfile>
    </MenuContainer>
  );
}


