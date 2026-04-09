import { CssBaseline, ThemeProvider } from '@mui/material'

import { AppRouter } from './app/router'
import { appTheme } from './app/theme'

function App() {
  return (
    <ThemeProvider theme={appTheme}>
      <CssBaseline />
      <AppRouter />
    </ThemeProvider>
  )
}

export default App
