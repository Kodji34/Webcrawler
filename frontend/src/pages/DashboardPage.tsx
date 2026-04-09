import { Stack, Typography } from '@mui/material'
import { useTranslation } from 'react-i18next'

import { DashboardOverview } from '../features/dashboard/DashboardOverview'

export function DashboardPage() {
  const { t } = useTranslation()

  return (
    <Stack spacing={3}>
      <Stack spacing={0.75}>
        <Typography variant="h4">{t('dashboard.heroTitle')}</Typography>
        <Typography variant="body2" color="text.secondary">
          {t('dashboard.heroSubtitle')}
        </Typography>
      </Stack>
      <DashboardOverview />
    </Stack>
  )
}
