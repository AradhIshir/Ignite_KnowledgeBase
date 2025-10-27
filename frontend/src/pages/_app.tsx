import type { AppProps } from 'next/app';
import { ThemeProvider, createGlobalStyle } from 'styled-components';
import { useEffect, useState } from 'react';
import { baseTheme, darkTheme } from '../styles/theme';

const GlobalStyle = createGlobalStyle`
  :root { color-scheme: light dark; }
  *, *::before, *::after { box-sizing: border-box; }
  html, body, #__next { height: 100%; }
  body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; background: ${(p) => p.theme.colors.background}; color: ${(p) => p.theme.colors.text}; }
  a { color: inherit; text-decoration: none; }
`;

export default function App({ Component, pageProps }: AppProps) {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('ignite-theme');
    setIsDark(saved === 'dark');
  }, []);

  const toggle = () => {
    const next = !isDark;
    setIsDark(next);
    localStorage.setItem('ignite-theme', next ? 'dark' : 'light');
  };

  useEffect(() => {
    (window as any).themeToggle = toggle;
    return () => {
      if ((window as any).themeToggle === toggle) {
        delete (window as any).themeToggle;
      }
    };
  }, [toggle]);

  return (
    <ThemeProvider theme={{ ...(isDark ? darkTheme : baseTheme), toggleTheme: toggle }}>
      <GlobalStyle />
      <Component {...pageProps} />
    </ThemeProvider>
  );
}

