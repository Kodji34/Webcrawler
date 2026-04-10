import { Stack, Typography } from '@mui/material'
import { useTranslation } from 'react-i18next'

import { WebImportWorkspace } from '../features/web-imports/WebImportWorkspace'

export function WebImportsPage() {
  const { t } = useTranslation()

  return (
    <Stack spacing={2.5}>
      <Stack spacing={0.75}>
        <Typography variant="h4">{t('web.heroTitle')}</Typography>
        <Typography variant="body2" color="text.secondary">
          {t('web.heroSubtitle')}
        </Typography>
      </Stack>
      <WebImportWorkspace />
    </Stack>
  )
}
