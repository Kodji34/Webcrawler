import { Stack, Typography } from '@mui/material'
import { useTranslation } from 'react-i18next'

import { ScientificSearchWorkspace } from '../features/scientific-search/ScientificSearchWorkspace'

export function ScientificSearchPage() {
  const { t } = useTranslation()

  return (
    <Stack spacing={2.5}>
      <Stack spacing={0.75}>
        <Typography variant="h3">{t('scientific.heroTitle')}</Typography>
        <Typography variant="body1" color="text.secondary">
          {t('scientific.heroSubtitle')}
        </Typography>
      </Stack>
      <ScientificSearchWorkspace />
    </Stack>
  )
}
