import AutoStoriesOutlinedIcon from '@mui/icons-material/AutoStoriesOutlined'
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined'
import {
  Alert,
  Box,
  Button,
  Chip,
  Checkbox,
  Link,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import { startTransition, useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'

import type {
  FullTextAcquisitionItem,
  FullTextSourceDescriptor,
  ScientificImportedRecord,
} from './scientificTypes'

function outcomeTone(outcome: FullTextAcquisitionItem['outcome']) {
  if (outcome === 'full_text_retrieved') {
    return 'success'
  }
  if (outcome === 'full_text_not_authorized') {
    return 'warning'
  }
  if (outcome === 'failed') {
    return 'error'
  }
  return 'default'
}

export function FullTextAcquisitionPanel() {
  const { t } = useTranslation()
  const [imports, setImports] = useState<ScientificImportedRecord[]>([])
  const [items, setItems] = useState<FullTextAcquisitionItem[]>([])
  const [sources, setSources] = useState<FullTextSourceDescriptor[]>([])
  const [selectedImportIds, setSelectedImportIds] = useState<string[]>([])
  const [activeImportId, setActiveImportId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAcquiring, setIsAcquiring] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [importsResponse, itemsResponse, sourcesResponse] = await Promise.all([
        fetch('/api/v1/scientific/imports'),
        fetch('/api/v1/fulltext/items'),
        fetch('/api/v1/fulltext/sources'),
      ])

      if (!importsResponse.ok || !itemsResponse.ok || !sourcesResponse.ok) {
        throw new Error('HTTP error')
      }

      const [importsPayload, itemsPayload, sourcesPayload] = await Promise.all([
        importsResponse.json() as Promise<ScientificImportedRecord[]>,
        itemsResponse.json() as Promise<{ items: FullTextAcquisitionItem[] }>,
        sourcesResponse.json() as Promise<FullTextSourceDescriptor[]>,
      ])

      startTransition(() => {
        setImports(importsPayload)
        setItems(itemsPayload.items)
        setSources(sourcesPayload)
        setActiveImportId((current) => current ?? importsPayload[0]?.import_id ?? null)
        setErrorMessage(null)
      })
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('scientific.errors.fullTextLoad'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadData()
  }, [])

  const latestByImportId = useMemo(() => {
    const mapping = new Map<string, FullTextAcquisitionItem>()
    for (const item of items) {
      mapping.set(item.scientific_import_id, item)
    }
    return mapping
  }, [items])

  const activeItem = useMemo(() => {
    if (!activeImportId) {
      return null
    }
    return latestByImportId.get(activeImportId) ?? null
  }, [activeImportId, latestByImportId])

  const allSelected =
    imports.length > 0 &&
    selectedImportIds.length > 0 &&
    selectedImportIds.length === imports.length

  const handleAcquire = async () => {
    if (!selectedImportIds.length) {
      return
    }

    setIsAcquiring(true)
    setSuccessMessage(null)
    setErrorMessage(null)

    try {
      const response = await fetch('/api/v1/fulltext/acquire-imports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          import_ids: selectedImportIds,
        }),
      })
      const payload = (await response.json()) as
        | { acquired_count?: number; items?: FullTextAcquisitionItem[]; detail?: string }
        | undefined
      if (!response.ok) {
        throw new Error(payload?.detail || `HTTP ${response.status}`)
      }

      setSuccessMessage(
        t('scientific.fullText.messages.acquired', {
          count: payload?.acquired_count ?? 0,
        }),
      )
      await loadData()
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : t('scientific.errors.fullTextAcquire'),
      )
    } finally {
      setIsAcquiring(false)
    }
  }

  return (
    <Paper sx={{ p: 2.25 }}>
      <Stack spacing={1.5}>
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          justifyContent="space-between"
          alignItems={{ xs: 'flex-start', md: 'center' }}
          spacing={1}
        >
          <Box>
            <Typography variant="h6">{t('scientific.fullText.title')}</Typography>
            <Typography variant="body2" color="text.secondary">
              {t('scientific.fullText.subtitle')}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1}>
            <Button
              variant="text"
              startIcon={<RefreshOutlinedIcon />}
              disabled={isLoading}
              onClick={() => void loadData()}
            >
              {t('scientific.fullText.refresh')}
            </Button>
            <Button
              variant="outlined"
              startIcon={<AutoStoriesOutlinedIcon />}
              disabled={!selectedImportIds.length || isAcquiring}
              onClick={handleAcquire}
            >
              {isAcquiring
                ? t('scientific.fullText.acquiring')
                : t('scientific.fullText.acquire')}
            </Button>
          </Stack>
        </Stack>

        {errorMessage ? <Alert severity="warning">{errorMessage}</Alert> : null}
        {successMessage ? <Alert severity="success">{successMessage}</Alert> : null}

        <Stack direction="row" spacing={1} flexWrap="wrap">
          {sources.map((source) => (
            <Chip
              key={source.key}
              size="small"
              variant="outlined"
              label={`${source.label}${source.requires_authentication ? ' | auth' : ''}`}
            />
          ))}
        </Stack>

        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={allSelected}
                  indeterminate={
                    selectedImportIds.length > 0 && selectedImportIds.length < imports.length
                  }
                  onChange={(_, checked) => {
                    setSelectedImportIds(checked ? imports.map((item) => item.import_id) : [])
                  }}
                />
              </TableCell>
              <TableCell>{t('scientific.fullText.columns.title')}</TableCell>
              <TableCell>{t('scientific.fullText.columns.source')}</TableCell>
              <TableCell>{t('scientific.fullText.columns.status')}</TableCell>
              <TableCell>{t('scientific.fullText.columns.access')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {imports.map((record) => {
              const currentItem = latestByImportId.get(record.import_id)
              const checked = selectedImportIds.includes(record.import_id)
              return (
                <TableRow
                  key={record.import_id}
                  hover
                  selected={activeImportId === record.import_id}
                  sx={{ cursor: 'pointer' }}
                  onClick={() => setActiveImportId(record.import_id)}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={checked}
                      onChange={(_, nextChecked) => {
                        setSelectedImportIds((current) =>
                          nextChecked
                            ? [...current, record.import_id]
                            : current.filter((item) => item !== record.import_id),
                        )
                      }}
                    />
                  </TableCell>
                  <TableCell sx={{ minWidth: 260 }}>
                    <Typography variant="body2" fontWeight={600}>
                      {record.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {record.journal || record.source}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip size="small" label={currentItem?.source ?? 'pending'} />
                  </TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      color={outcomeTone(currentItem?.outcome ?? 'metadata_only')}
                      label={t(`scientific.fullText.outcomes.${currentItem?.outcome ?? 'metadata_only'}`)}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {currentItem
                        ? t(`scientific.fullText.access.${currentItem.access_mode}`)
                        : '-'}
                    </Typography>
                  </TableCell>
                </TableRow>
              )
            })}
            {!imports.length ? (
              <TableRow>
                <TableCell colSpan={5}>
                  <Typography variant="body2" color="text.secondary">
                    {isLoading
                      ? t('scientific.fullText.loading')
                      : t('scientific.fullText.empty')}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>

        <Box>
          <Typography variant="subtitle1" fontWeight={600}>
            {t('scientific.fullText.previewTitle')}
          </Typography>
          {activeItem ? (
            <Stack spacing={1}>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                <Chip
                  size="small"
                  color={outcomeTone(activeItem.outcome)}
                  label={t(`scientific.fullText.outcomes.${activeItem.outcome}`)}
                />
                <Chip
                  size="small"
                  variant="outlined"
                  label={t(`scientific.fullText.access.${activeItem.access_mode}`)}
                />
                {activeItem.license_name ? (
                  <Chip size="small" variant="outlined" label={activeItem.license_name} />
                ) : null}
              </Stack>
              <Typography variant="body2" color="text.secondary">
                {activeItem.excerpt || t('scientific.fullText.noText')}
              </Typography>
              {activeItem.full_text_url ? (
                <Link href={activeItem.full_text_url} target="_blank" rel="noreferrer">
                  {t('scientific.fullText.open')}
                </Link>
              ) : null}
              {activeItem.notes.map((note) => (
                <Typography key={note} variant="caption" color="text.secondary">
                  {note}
                </Typography>
              ))}
            </Stack>
          ) : (
            <Typography variant="body2" color="text.secondary">
              {t('scientific.fullText.noPreview')}
            </Typography>
          )}
        </Box>
      </Stack>
    </Paper>
  )
}
