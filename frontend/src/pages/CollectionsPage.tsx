import { Stack, Typography } from '@mui/material'
import { useTranslation } from 'react-i18next'

import { CorpusWorkspace } from '../features/corpus/CorpusWorkspace'

export function CollectionsPage() {
  const { t } = useTranslation()

  return (
    <Stack spacing={2.5}>
      <Stack spacing={0.75}>
        <Typography variant="h4">{t('corpus.heroTitle')}</Typography>
        <Typography variant="body2" color="text.secondary">
          {t('corpus.heroSubtitle')}
        </Typography>
      </Stack>
      <CorpusWorkspace />
    </Stack>
  )
}
