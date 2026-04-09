import TranslateOutlinedIcon from '@mui/icons-material/TranslateOutlined'
import { Stack, ToggleButton, ToggleButtonGroup, Typography } from '@mui/material'
import type { MouseEvent } from 'react'
import { useTranslation } from 'react-i18next'

import { languageStorageKey } from '../i18n/config'

export function LanguageToggle() {
  const { i18n, t } = useTranslation()

  const handleLanguageChange = async (
    _event: MouseEvent<HTMLElement>,
    nextLanguage: string | null,
  ) => {
    if (!nextLanguage || nextLanguage === i18n.language) {
      return
    }

    window.localStorage.setItem(languageStorageKey, nextLanguage)
    await i18n.changeLanguage(nextLanguage)
  }

  return (
    <Stack direction="row" spacing={1.5} alignItems="center">
      <TranslateOutlinedIcon fontSize="small" />
      <Typography variant="body2">{t('actions.language')}</Typography>
      <ToggleButtonGroup
        exclusive
        size="small"
        color="primary"
        value={i18n.language}
        onChange={handleLanguageChange}
      >
        <ToggleButton value="en">EN</ToggleButton>
        <ToggleButton value="fr">FR</ToggleButton>
      </ToggleButtonGroup>
    </Stack>
  )
}
