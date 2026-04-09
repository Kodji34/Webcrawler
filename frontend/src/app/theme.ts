import { createTheme } from '@mui/material/styles'

export const appTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0f5c5c',
      dark: '#0a4444',
      light: '#4d8d8d',
    },
    secondary: {
      main: '#b86a32',
      dark: '#884b1c',
      light: '#d38a58',
    },
    background: {
      default: '#f5efe5',
      paper: 'rgba(255, 251, 246, 0.92)',
    },
    text: {
      primary: '#102326',
      secondary: '#4d5c5f',
    },
    success: {
      main: '#1f8a55',
    },
    warning: {
      main: '#c77f1c',
    },
  },
  shape: {
    borderRadius: 18,
  },
  typography: {
    fontFamily: '"IBM Plex Sans", sans-serif',
    h1: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 700,
      letterSpacing: '-0.04em',
    },
    h2: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 700,
      letterSpacing: '-0.03em',
    },
    h3: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 700,
    },
    h4: {
      fontFamily: '"Space Grotesk", sans-serif',
      fontWeight: 700,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          border: '1px solid rgba(16, 35, 38, 0.08)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 18px 45px rgba(16, 35, 38, 0.08)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
        },
      },
    },
  },
})
