import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined'
import BoltOutlinedIcon from '@mui/icons-material/BoltOutlined'
import DnsOutlinedIcon from '@mui/icons-material/DnsOutlined'
import LanguageOutlinedIcon from '@mui/icons-material/LanguageOutlined'
import ViewKanbanOutlinedIcon from '@mui/icons-material/ViewKanbanOutlined'
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined'
import {
  Alert,
  Box,
  Chip,
  Grid,
  List,
  ListItem,
  Paper,
  Stack,
  Typography,
} from '@mui/material'
import { startTransition, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { useTranslation } from 'react-i18next'

type HealthPayload = {
  phase: { number: number; name: string; focus: string }
  services: {
    api: string
    frontend: string
    postgres: string
    redis: string
    celery_broker: string
    celery_queue: string
  }
}

type StatusCardProps = {
  icon: ReactNode
  title: string
  value: string
  caption: string
}

function StatusCard({ icon, title, value, caption }: StatusCardProps) {
  return (
    <Paper className="rise-in" sx={{ p: 2.25, height: '100%' }}>
      <Stack spacing={1}>
        <Stack direction="row" spacing={1.2} alignItems="center">
          <Box
            sx={{
              display: 'grid',
              placeItems: 'center',
              width: 38,
              height: 38,
              borderRadius: '10px',
              bgcolor: 'rgba(29, 111, 214, 0.09)',
              color: 'primary.main',
            }}
          >
            {icon}
          </Box>
          <Typography variant="subtitle1" fontWeight={700}>
            {title}
          </Typography>
        </Stack>
        <Typography variant="h5">{value}</Typography>
        <Typography variant="body2" color="text.secondary">
          {caption}
        </Typography>
      </Stack>
    </Paper>
  )
}

export function DashboardOverview() {
  const { t } = useTranslation()
  const [health, setHealth] = useState<HealthPayload | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    const loadHealth = async () => {
      try {
        const response = await fetch('/api/v1/health', { signal: controller.signal })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const payload = (await response.json()) as HealthPayload
        startTransition(() => {
          setHealth(payload)
          setLoadError(null)
        })
      } catch (error) {
        if (controller.signal.aborted) {
          return
        }

        startTransition(() => {
          setHealth(null)
          setLoadError(
            error instanceof Error ? error.message : t('dashboard.backendUnavailable'),
          )
        })
      }
    }

    void loadHealth()

    return () => controller.abort()
  }, [t])

  const phaseName = health?.phase.name ?? t('dashboard.offlinePhaseName')
  const queueName = health?.services.celery_queue ?? 'research-default'

  return (
    <Stack spacing={3}>
      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12, md: 6, xl: 3 }}>
          <StatusCard
            icon={<DnsOutlinedIcon />}
            title={t('dashboard.cards.api.title')}
            value={health?.services.api ?? t('dashboard.offline')}
            caption={t('dashboard.cards.api.caption')}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6, xl: 3 }}>
          <StatusCard
            icon={<BoltOutlinedIcon />}
            title={t('dashboard.cards.worker.title')}
            value={queueName}
            caption={t('dashboard.cards.worker.caption')}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6, xl: 3 }}>
          <StatusCard
            icon={<LanguageOutlinedIcon />}
            title={t('dashboard.cards.i18n.title')}
            value="EN / FR"
            caption={t('dashboard.cards.i18n.caption')}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6, xl: 3 }}>
          <StatusCard
            icon={<ViewKanbanOutlinedIcon />}
            title={t('dashboard.cards.phase.title')}
            value={phaseName}
            caption={t('dashboard.cards.phase.caption')}
          />
        </Grid>
      </Grid>

      {loadError ? (
        <Alert severity="warning" icon={<WarningAmberOutlinedIcon />}>
          {t('dashboard.backendWarning', { details: loadError })}
        </Alert>
      ) : null}

      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12, lg: 7 }}>
          <Paper className="rise-in" sx={{ p: 3 }}>
            <Stack spacing={2}>
              <Stack direction="row" spacing={1} alignItems="center">
                <AutoAwesomeOutlinedIcon color="primary" />
                <Typography variant="h6">{t('dashboard.scopeTitle')}</Typography>
                <Chip label={t('dashboard.phase1Chip')} size="small" color="primary" />
              </Stack>
              <Typography color="text.secondary">
                {health?.phase.focus ?? t('dashboard.scopeFallback')}
              </Typography>
              <List sx={{ p: 0 }}>
                {(t('dashboard.scopeChecklist', { returnObjects: true }) as string[]).map(
                  (item) => (
                    <ListItem key={item} sx={{ px: 0, py: 0.5 }}>
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '999px',
                          bgcolor: 'primary.main',
                          mr: 1.5,
                          flexShrink: 0,
                        }}
                      />
                      <Typography variant="body2">{item}</Typography>
                    </ListItem>
                  ),
                )}
              </List>
            </Stack>
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, lg: 5 }}>
          <Paper className="rise-in" sx={{ p: 3, height: '100%' }}>
            <Stack spacing={2.25}>
              <Typography variant="h6">{t('dashboard.stackTitle')}</Typography>
              <Stack spacing={1.25}>
                <Typography variant="body2" color="text.secondary">
                  {t('dashboard.stack.api')}
                </Typography>
                <Typography variant="body1">
                  {health?.services.api ?? 'http://127.0.0.1:8000'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('dashboard.stack.postgres')}
                </Typography>
                <Typography variant="body1">
                  {health?.services.postgres ??
                    'postgresql+psycopg://postgres:postgres@127.0.0.1:5432/pycrawler'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('dashboard.stack.redis')}
                </Typography>
                <Typography variant="body1">
                  {health?.services.redis ?? 'redis://127.0.0.1:6379/0'}
                </Typography>
              </Stack>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  )
}
