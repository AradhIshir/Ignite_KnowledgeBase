import Link from 'next/link';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const LandingWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  background: linear-gradient(180deg, #1e3a8a 0%, #0ea5e9 100%);
  overflow: hidden;
`;

const Content = styled(motion.div)`
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 900px;
  width: 100%;
`;

const LogoContainer = styled(motion.div)`
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  
  @media (max-width: 768px) {
    margin-bottom: 24px;
  }
`;

const Logo = styled.div`
  width: 80px;
  height: 80px;
  background: #1e40af;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  
  @media (max-width: 768px) {
    width: 64px;
    height: 64px;
    border-radius: 12px;
  }
`;

const BookStack = styled.div`
  position: relative;
  width: 50px;
  height: 40px;
  
  @media (max-width: 768px) {
    width: 40px;
    height: 32px;
  }
`;

const Book = styled.div<{ $color: string; $top: string; $left: string; $rotation: string; $zIndex: number }>`
  position: absolute;
  width: 35px;
  height: 28px;
  background: ${props => props.$color};
  border-radius: 2px;
  top: ${props => props.$top};
  left: ${props => props.$left};
  transform: rotate(${props => props.$rotation});
  z-index: ${props => props.$zIndex};
  box-shadow: 
    0 2px 4px rgba(0, 0, 0, 0.2),
    inset -2px 0 0 rgba(0, 0, 0, 0.1);
  
  &::after {
    content: '';
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: white;
    border-radius: 0 2px 2px 0;
  }
  
  @media (max-width: 768px) {
    width: 28px;
    height: 22px;
  }
`;

const Title = styled(motion.h1)`
  font-size: 5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 32px 0;
  letter-spacing: -0.02em;
  line-height: 1.1;
  font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
  
  @media (max-width: 768px) {
    font-size: 3.5rem;
    margin-bottom: 24px;
  }
  
  @media (max-width: 480px) {
    font-size: 2.5rem;
  }
`;

const Subtitle = styled(motion.p)`
  font-size: 1.5rem;
  color: white;
  margin: 0 0 64px 0;
  line-height: 1.6;
  font-weight: 400;
  font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
  
  @media (max-width: 768px) {
    font-size: 1.25rem;
    margin-bottom: 48px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.125rem;
    margin-bottom: 40px;
  }
`;

const ButtonRow = styled(motion.div)`
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  align-items: center;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
`;

const SignInButton = styled(motion.a)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 16px 40px;
  background: #1e40af;
  color: white;
  border-radius: 12px;
  font-size: 1.125rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
  
  &:hover {
    background: #1e3a8a;
    transform: translateY(-2px);
  }
  
  @media (max-width: 768px) {
    width: 100%;
    padding: 18px 32px;
  }
`;

const SignUpButton = styled(motion.a)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 16px 40px;
  background: #1e40af;
  color: white;
  border-radius: 12px;
  font-size: 1.125rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
  
  &:hover {
    background: #1e3a8a;
    transform: translateY(-2px);
  }
  
  @media (max-width: 768px) {
    width: 100%;
    padding: 18px 32px;
  }
`;

export default function Landing() {
  return (
    <LandingWrapper>
      <Content
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <LogoContainer
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Logo>
            <BookStack>
              <Book $color="#10b981" $top="0px" $left="8px" $rotation="2deg" $zIndex={3} />
              <Book $color="#ef4444" $top="8px" $left="6px" $rotation="-1deg" $zIndex={2} />
              <Book $color="#3b82f6" $top="16px" $left="4px" $rotation="1deg" $zIndex={1} />
            </BookStack>
          </Logo>
        </LogoContainer>
        
        <Title
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Knowledge Hub
        </Title>
        
        <Subtitle
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          Your journey to discover your projects' knowledge. All documents assembled at one place
        </Subtitle>
        
        <ButtonRow
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Link href="/auth/signin" passHref legacyBehavior>
            <SignInButton
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Sign In
            </SignInButton>
          </Link>
          <Link href="/auth/signup" passHref legacyBehavior>
            <SignUpButton
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              New to KnowledgeHub- Sign Up!
            </SignUpButton>
          </Link>
        </ButtonRow>
      </Content>
    </LandingWrapper>
  );
}
