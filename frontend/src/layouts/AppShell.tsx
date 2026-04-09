import MenuRoundedIcon from '@mui/icons-material/MenuRounded'
import {
  AppBar,
  Box,
  Chip,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import { useMemo, useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

import { navigationItems } from '../app/navigation'
import { LanguageToggle } from '../components/LanguageToggle'

const drawerWidth = 272

export function AppShell() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const theme = useTheme()
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'))
  const [mobileOpen, setMobileOpen] = useState(false)

  const activeItem = useMemo(
    () =>
      navigationItems.find((item) =>
        item.path === '/'
          ? location.pathname === '/'
          : location.pathname.startsWith(item.path),
      ) ?? navigationItems[0],
    [location.pathname],
  )

  const drawerContent = (
    <Stack sx={{ height: '100%', p: 2 }}>
      <Box
        sx={{
          p: 2.25,
          borderRadius: 3,
          color: 'common.white',
          background:
            'linear-gradient(160deg, rgba(29, 111, 214, 0.98) 0%, rgba(21, 82, 160, 0.96) 100%)',
        }}
      >
        <Chip
          label={t('app.phaseLabel')}
          size="small"
          sx={{
            bgcolor: 'rgba(255,255,255,0.18)',
            color: 'common.white',
            mb: 2,
          }}
        />
        <Typography variant="h5" sx={{ mb: 0.75 }}>
          {t('app.title')}
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.82 }}>
          {t('app.tagline')}
        </Typography>
      </Box>

      <List sx={{ mt: 2, flexGrow: 1 }}>
        {navigationItems.map((item) => {
          const Icon = item.icon
          const selected =
            item.path === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(item.path)

          return (
            <ListItemButton
              key={item.key}
              selected={selected}
              sx={{
                mb: 0.5,
                borderRadius: 2.5,
              }}
              onClick={() => {
                navigate(item.path)
                setMobileOpen(false)
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <Icon color={selected ? 'primary' : 'inherit'} />
              </ListItemIcon>
              <ListItemText primary={t(`nav.${item.key}`)} />
            </ListItemButton>
          )
        })}
      </List>

      <Box
        sx={{
          p: 1.75,
          borderRadius: 2.5,
          bgcolor: 'rgba(29, 111, 214, 0.06)',
          border: '1px solid rgba(29, 111, 214, 0.12)',
        }}
      >
        <Typography variant="subtitle2" sx={{ mb: 0.6 }}>
          {t('app.phaseBoundaryTitle')}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {t('app.phaseBoundaryBody')}
        </Typography>
      </Box>
    </Stack>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        color="transparent"
        elevation={0}
        sx={{
          width: { lg: `calc(100% - ${drawerWidth}px)` },
          ml: { lg: `${drawerWidth}px` },
          backdropFilter: 'blur(12px)',
          backgroundColor: 'rgba(255, 255, 255, 0.74)',
          borderBottom: '1px solid rgba(29, 111, 214, 0.08)',
        }}
      >
        <Toolbar sx={{ gap: 2, minHeight: 72 }}>
          {!isDesktop ? (
            <IconButton color="inherit" onClick={() => setMobileOpen((open) => !open)}>
              <MenuRoundedIcon />
            </IconButton>
          ) : null}
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6">{t(`nav.${activeItem.key}`)}</Typography>
            <Typography variant="body2" color="text.secondary">
              {t(`headers.${activeItem.key}`)}
            </Typography>
          </Box>
          <Chip color="success" size="small" label={t('app.localLabel')} />
          <LanguageToggle />
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{
          width: { lg: drawerWidth },
          flexShrink: { lg: 0 },
        }}
      >
        <Drawer
          variant={isDesktop ? 'permanent' : 'temporary'}
          open={isDesktop ? true : mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              borderRight: '1px solid rgba(29, 111, 214, 0.08)',
              background:
                'linear-gradient(180deg, rgba(250, 252, 255, 0.98) 0%, rgba(238, 243, 249, 0.96) 100%)',
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          px: { xs: 2, md: 4 },
          py: { xs: 11, md: 12 },
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
