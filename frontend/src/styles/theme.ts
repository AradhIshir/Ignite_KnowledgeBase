export const baseTheme = {
  colors: {
    background: 'linear-gradient(180deg, #E6F4F1 0%, #EAF3FF 100%)',
    surface: '#ffffff',
    text: '#0F2A43',
    primary: '#1D74F5', // blue
    secondary: '#22C7A9', // light green
    accent: '#FF6B6B',
    muted: '#6B7A90',
    border: '#D7E2EE',
    cardBg: 'rgba(255,255,255,0.85)'
  },
  radii: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px'
  },
  shadows: {
    sm: '0 2px 8px rgba(0,0,0,0.06)',
    md: '0 8px 24px rgba(16, 38, 73, 0.12)'
  },
  transitions: {
    base: '200ms ease'
  }
} as const;

export const darkTheme = {
  ...baseTheme,
  colors: {
    ...baseTheme.colors,
    background: 'linear-gradient(180deg, #0E1726 0%, #0D1B2A 100%)',
    surface: '#0F253E',
    text: '#EAF3FF',
    cardBg: 'rgba(19,33,53,0.85)',
    border: '#1E3A5C'
  }
} as const;

export type Theme = typeof baseTheme & { toggleTheme?: () => void };

