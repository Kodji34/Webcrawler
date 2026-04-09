import { Stack, Typography } from '@mui/material'
import { useTranslation } from 'react-i18next'

import { DashboardOverview } from '../features/dashboard/DashboardOverview'

export function DashboardPage() {
  const { t } = useTranslation()

  return (
    <Stack spacing={3}>
      <Stack spacing={1}>
        <Typography variant="h2">{t('app.title')}</Typography>
        <Typography variant="body1" color="text.secondary">
          {t('app.tagline')}
        </Typography>
      </Stack>
      <DashboardOverview />
    </Stack>
  )
}
