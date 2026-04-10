import CloudDownloadOutlinedIcon from '@mui/icons-material/CloudDownloadOutlined'
import {
  Alert,
  Box,
  Button,
  Chip,
  Link,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { startTransition, useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'

import type { WebImportedArticle, WebImportStatus } from './webTypes'

function statusTone(status: WebImportStatus) {
  if (status === 'text_retrieved') {
    return 'success'
  }
  if (status === 'not_authorized') {
    return 'warning'
  }
  if (status === 'failed') {
    return 'error'
  }
  return 'default'
}

export function WebImportWorkspace() {
  const { t } = useTranslation()
  const [urlList, setUrlList] = useState('')
  const [language, setLanguage] = useState('')
  const [items, setItems] = useState<WebImportedArticle[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isImporting, setIsImporting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const activeItem = useMemo(
    () => items.find((item) => item.item_id === activeId) ?? items[0] ?? null,
    [activeId, items],
  )

  const loadItems = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/v1/web/items')
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const payload = (await response.json()) as { items: WebImportedArticle[] }
      startTransition(() => {
        setItems(payload.items)
        setActiveId((current) => current ?? payload.items[0]?.item_id ?? null)
        setErrorMessage(null)
      })
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('web.errors.load'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadItems()
  }, [])

  const handleImport = async () => {
    const urls = urlList
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)
    if (!urls.length) {
      return
    }

    setIsImporting(true)
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      const response = await fetch('/api/v1/web/import-urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: t('web.defaultProject'),
          entries: urls.map((url) => ({
            url,
            language: language.trim() || undefined,
          })),
        }),
      })
      const payload = (await response.json()) as {
        imported_count?: number
        text_retrieved_count?: number
        detail?: string
      }
      if (!response.ok) {
        throw new Error(payload.detail || `HTTP ${response.status}`)
      }
      setSuccessMessage(
        t('web.messages.imported', {
          count: payload.imported_count ?? urls.length,
          text: payload.text_retrieved_count ?? 0,
        }),
      )
      setUrlList('')
      await loadItems()
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('web.errors.import'))
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <Stack spacing={2}>
      {errorMessage ? <Alert severity="warning">{errorMessage}</Alert> : null}
      {successMessage ? <Alert severity="success">{successMessage}</Alert> : null}

      <Paper sx={{ p: 2.25 }}>
        <Stack spacing={1.5}>
          <Typography variant="h6">{t('web.formTitle')}</Typography>
          <Typography variant="body2" color="text.secondary">
            {t('web.formHelp')}
          </Typography>
          <TextField
            label={t('web.fields.urls')}
            value={urlList}
            multiline
            minRows={5}
            onChange={(event) => setUrlList(event.target.value)}
          />
          <TextField
            label={t('web.fields.language')}
            value={language}
            size="small"
            placeholder="fr / en"
            onChange={(event) => setLanguage(event.target.value)}
            sx={{ maxWidth: 220 }}
          />
          <Box>
            <Button
              variant="contained"
              startIcon={<CloudDownloadOutlinedIcon />}
              disabled={!urlList.trim() || isImporting}
              onClick={handleImport}
            >
              {isImporting ? t('web.importing') : t('web.import')}
            </Button>
          </Box>
        </Stack>
      </Paper>

      <Paper sx={{ p: 2.25 }}>
        <Stack spacing={1.5}>
          <Box>
            <Typography variant="h6">{t('web.resultsTitle')}</Typography>
            <Typography variant="body2" color="text.secondary">
              {t('web.resultsSummary', { count: items.length })}
            </Typography>
          </Box>

          <TableContainer sx={{ maxHeight: 360, border: (theme) => `1px solid ${theme.palette.divider}`, borderRadius: 2 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>{t('web.columns.title')}</TableCell>
                  <TableCell>{t('web.columns.domain')}</TableCell>
                  <TableCell>{t('web.columns.status')}</TableCell>
                  <TableCell>{t('web.columns.language')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {items.map((item) => (
                  <TableRow
                    key={item.item_id}
                    hover
                    selected={activeItem?.item_id === item.item_id}
                    sx={{ cursor: 'pointer' }}
                    onClick={() => setActiveId(item.item_id)}
                  >
                    <TableCell sx={{ minWidth: 260 }}>
                      <Typography variant="body2" fontWeight={600}>
                        {item.title || item.label || item.url}
                      </Typography>
                      <Link href={item.url} target="_blank" rel="noreferrer" variant="caption">
                        {item.url}
                      </Link>
                    </TableCell>
                    <TableCell>{item.source_domain || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        color={statusTone(item.status)}
                        label={t(`web.status.${item.status}`)}
                      />
                    </TableCell>
                    <TableCell>{item.language || '-'}</TableCell>
                  </TableRow>
                ))}
                {!items.length ? (
                  <TableRow>
                    <TableCell colSpan={4}>
                      <Typography variant="body2" color="text.secondary">
                        {isLoading ? t('web.loading') : t('web.empty')}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : null}
              </TableBody>
            </Table>
          </TableContainer>
        </Stack>
      </Paper>

      <Paper sx={{ p: 2.25 }}>
        <Stack spacing={1}>
          <Typography variant="h6">{t('web.previewTitle')}</Typography>
          {activeItem ? (
            <>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Chip
                  size="small"
                  color={statusTone(activeItem.status)}
                  label={t(`web.status.${activeItem.status}`)}
                />
                {activeItem.content_type ? (
                  <Chip size="small" variant="outlined" label={activeItem.content_type} />
                ) : null}
              </Stack>
              <Typography variant="body2" color="text.secondary">
                {activeItem.excerpt || activeItem.description || t('web.noText')}
              </Typography>
              {activeItem.notes.map((note) => (
                <Typography key={note} variant="caption" color="text.secondary">
                  {note}
                </Typography>
              ))}
            </>
          ) : (
            <Typography variant="body2" color="text.secondary">
              {t('web.noPreview')}
            </Typography>
          )}
        </Stack>
      </Paper>
    </Stack>
  )
}
