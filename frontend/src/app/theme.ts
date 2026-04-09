import { createTheme } from '@mui/material/styles'

export const appTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1d6fd6',
      dark: '#1552a0',
      light: '#5d97e8',
    },
    secondary: {
      main: '#7f8ea3',
      dark: '#586577',
      light: '#aeb8c5',
    },
    background: {
      default: '#eef3f9',
      paper: 'rgba(255, 255, 255, 0.94)',
    },
    text: {
      primary: '#172435',
      secondary: '#607086',
    },
    success: {
      main: '#2c8f62',
    },
    warning: {
      main: '#d18a2b',
    },
  },
  shape: {
    borderRadius: 10,
  },
  typography: {
    fontFamily: '"Manrope", "IBM Plex Sans", sans-serif',
    h1: {
      fontFamily: '"Manrope", "Space Grotesk", sans-serif',
      fontWeight: 700,
      fontSize: '2.6rem',
      letterSpacing: '-0.04em',
    },
    h2: {
      fontFamily: '"Manrope", "Space Grotesk", sans-serif',
      fontWeight: 700,
      fontSize: '2.1rem',
      letterSpacing: '-0.03em',
    },
    h3: {
      fontFamily: '"Manrope", "Space Grotesk", sans-serif',
      fontWeight: 700,
      fontSize: '1.6rem',
    },
    h4: {
      fontFamily: '"Manrope", "Space Grotesk", sans-serif',
      fontWeight: 700,
      fontSize: '1.3rem',
    },
    h5: {
      fontFamily: '"Manrope", "Space Grotesk", sans-serif',
      fontWeight: 700,
      fontSize: '1.1rem',
    },
    h6: {
      fontWeight: 700,
      fontSize: '0.98rem',
    },
    body1: {
      fontSize: '0.96rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.88rem',
      lineHeight: 1.55,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      fontSize: '0.9rem',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          border: '1px solid rgba(29, 111, 214, 0.08)',
          backdropFilter: 'blur(12px)',
          boxShadow: '0 14px 36px rgba(23, 36, 53, 0.08)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 9,
        },
      },
    },
  },
})
