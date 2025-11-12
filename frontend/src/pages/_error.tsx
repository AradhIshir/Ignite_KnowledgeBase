import { NextPageContext } from 'next';
import styled from 'styled-components';
import Link from 'next/link';

const ErrorWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(180deg, #E6F4F1 0%, #EAF3FF 100%);
`;

const ErrorCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 48px;
  max-width: 600px;
  width: 100%;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const ErrorCode = styled.h1`
  font-size: 4rem;
  font-weight: 700;
  color: #1D74F5;
  margin: 0 0 16px 0;
`;

const ErrorMessage = styled.p`
  font-size: 1.25rem;
  color: #6b7280;
  margin: 0 0 32px 0;
`;

const HomeButton = styled(Link)`
  display: inline-block;
  padding: 12px 24px;
  background: #1D74F5;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s;

  &:hover {
    background: #1565D8;
  }
`;

interface ErrorProps {
  statusCode?: number;
}

function Error({ statusCode }: ErrorProps) {
  return (
    <ErrorWrapper>
      <ErrorCard>
        <ErrorCode>{statusCode || 'Error'}</ErrorCode>
        <ErrorMessage>
          {statusCode === 404
            ? 'The page you are looking for does not exist.'
            : 'An error occurred on the server.'}
        </ErrorMessage>
        <HomeButton href="/">Go Home</HomeButton>
      </ErrorCard>
    </ErrorWrapper>
  );
}

Error.getInitialProps = ({ res, err }: NextPageContext) => {
  const statusCode = res ? res.statusCode : err ? (err as any).statusCode : 404;
  return { statusCode };
};

export default Error;

