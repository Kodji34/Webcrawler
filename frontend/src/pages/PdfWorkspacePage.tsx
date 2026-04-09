import { Stack, Typography } from '@mui/material'
import { useTranslation } from 'react-i18next'

import { PdfWorkspace } from '../features/pdf-workspace/PdfWorkspace'

export function PdfWorkspacePage() {
  const { t } = useTranslation()

  return (
    <Stack spacing={2.5}>
      <Stack spacing={0.75}>
        <Typography variant="h4">{t('pdf.heroTitle')}</Typography>
        <Typography variant="body2" color="text.secondary">
          {t('pdf.heroSubtitle')}
        </Typography>
      </Stack>
      <PdfWorkspace />
    </Stack>
  )
}
