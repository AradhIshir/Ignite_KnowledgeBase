import Link from 'next/link';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const Wrapper = styled.div`
  display: flex; align-items: center; justify-content: center; height: 100%; padding: 24px;
`;
const Card = styled(motion.div)`
  background: ${(p) => p.theme.colors.cardBg};
  backdrop-filter: blur(8px);
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: ${(p) => p.theme.radii.xl};
  box-shadow: ${(p) => p.theme.shadows.md};
  padding: 32px; max-width: 720px; width: 100%;
`;
const Title = styled.h1`
  margin: 0 0 8px; color: ${(p) => p.theme.colors.primary};
`;
const Subtitle = styled.p`
  margin: 0 0 24px; color: ${(p) => p.theme.colors.muted};
`;
const Row = styled.div`
  display: flex; gap: 12px; flex-wrap: wrap;
`;
const Button = styled(motion.a)`
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px 16px; border-radius: ${(p) => p.theme.radii.lg}; cursor: pointer;
  background: ${(p) => p.theme.colors.primary}; color: white; border: none;
`;

export default function Landing() {
  return (
    <Wrapper>
      <Card initial={{ y: 12, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.4 }}>
        <Title>Ignite Knowledge</Title>
        <Subtitle>Search, organize, and share your team knowledge with ease.</Subtitle>
        <Row>
          <Link href="/auth/signin" passHref legacyBehavior>
            <Button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>Sign in</Button>
          </Link>
          <Link href="/app/dashboard" passHref legacyBehavior>
            <Button style={{ background: '#22C7A9' }} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>Go to app</Button>
          </Link>
        </Row>
      </Card>
    </Wrapper>
  );
}

