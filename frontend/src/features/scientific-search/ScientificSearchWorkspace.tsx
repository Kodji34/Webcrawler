import LaunchOutlinedIcon from '@mui/icons-material/LaunchOutlined'
import PlaylistAddCheckCircleOutlinedIcon from '@mui/icons-material/PlaylistAddCheckCircleOutlined'
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined'
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  FormControl,
  Grid,
  InputLabel,
  Link,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { startTransition, useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'

import type {
  IdentifierType,
  ScientificSearchResponse,
  ScientificSearchResult,
  ScientificSourceDescriptor,
  ScientificSourceKey,
} from './scientificTypes'

type SearchFormState = {
  source: ScientificSourceKey
  query: string
  identifier: string
  identifierType: IdentifierType | ''
  startDate: string
  endDate: string
  maxResults: number
  language: string
}

const initialForm: SearchFormState = {
  source: 'crossref',
  query: '',
  identifier: '',
  identifierType: '',
  startDate: '',
  endDate: '',
  maxResults: 10,
  language: '',
}

function resultKey(result: ScientificSearchResult) {
  return `${result.source}-${result.doi ?? result.pmid ?? result.url ?? result.title}`
}

export function ScientificSearchWorkspace() {
  const { t } = useTranslation()
  const [sources, setSources] = useState<ScientificSourceDescriptor[]>([])
  const [form, setForm] = useState<SearchFormState>(initialForm)
  const [results, setResults] = useState<ScientificSearchResult[]>([])
  const [selectedKeys, setSelectedKeys] = useState<string[]>([])
  const [activeKey, setActiveKey] = useState<string | null>(null)
  const [isLoadingSources, setIsLoadingSources] = useState(true)
  const [isSearching, setIsSearching] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [importMessage, setImportMessage] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    const loadSources = async () => {
      setIsLoadingSources(true)
      try {
        const response = await fetch('/api/v1/scientific/sources', {
          signal: controller.signal,
        })
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const payload = (await response.json()) as ScientificSourceDescriptor[]
        startTransition(() => {
          setSources(payload)
          if (payload[0]) {
            setForm((current) => ({ ...current, source: payload[0].key }))
          }
          setErrorMessage(null)
        })
      } catch (error) {
        if (!controller.signal.aborted) {
          setErrorMessage(
            error instanceof Error ? error.message : t('scientific.errors.sources'),
          )
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingSources(false)
        }
      }
    }

    void loadSources()
    return () => controller.abort()
  }, [t])

  const activeSource = useMemo(
    () => sources.find((source) => source.key === form.source) ?? null,
    [form.source, sources],
  )

  const selectedResults = useMemo(
    () => results.filter((result) => selectedKeys.includes(resultKey(result))),
    [results, selectedKeys],
  )

  const activeResult = useMemo(() => {
    if (activeKey) {
      return results.find((result) => resultKey(result) === activeKey) ?? null
    }
    return results[0] ?? null
  }, [activeKey, results])

  const allSelected =
    results.length > 0 && selectedKeys.length > 0 && selectedKeys.length === results.length

  const handleSourceChange = (nextSource: ScientificSourceKey) => {
    const source = sources.find((item) => item.key === nextSource)
    setForm((current) => ({
      ...current,
      source: nextSource,
      identifier:
        source && current.identifierType && source.supported_identifiers.includes(current.identifierType)
          ? current.identifier
          : '',
      identifierType:
        source && current.identifierType && source.supported_identifiers.includes(current.identifierType)
          ? current.identifierType
          : '',
      language: source?.supports_language ? current.language : '',
      startDate: source?.supports_date_range ? current.startDate : '',
      endDate: source?.supports_date_range ? current.endDate : '',
    }))
  }

  const handleSearch = async () => {
    setIsSearching(true)
    setImportMessage(null)
    setErrorMessage(null)

    try {
      const requestBody = {
        source: form.source,
        query: form.query.trim() || undefined,
        identifier: form.identifier.trim() || undefined,
        identifier_type: form.identifierType || undefined,
        start_date: activeSource?.supports_date_range && form.startDate ? form.startDate : undefined,
        end_date: activeSource?.supports_date_range && form.endDate ? form.endDate : undefined,
        max_results: form.maxResults,
        language: activeSource?.supports_language && form.language ? form.language : undefined,
      }

      const response = await fetch('/api/v1/scientific/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      const data = (await response.json()) as ScientificSearchResponse | { detail?: string }
      if (!response.ok) {
        throw new Error('detail' in data && data.detail ? data.detail : `HTTP ${response.status}`)
      }
      const payload = data as ScientificSearchResponse

      startTransition(() => {
        setResults(payload.results)
        setSelectedKeys([])
        setActiveKey(payload.results[0] ? resultKey(payload.results[0]) : null)
      })
    } catch (error) {
      setResults([])
      setSelectedKeys([])
      setActiveKey(null)
      setErrorMessage(
        error instanceof Error ? error.message : t('scientific.errors.search'),
      )
    } finally {
      setIsSearching(false)
    }
  }

  const handleImport = async () => {
    if (!selectedResults.length) {
      return
    }

    setIsImporting(true)
    setErrorMessage(null)
    setImportMessage(null)

    try {
      const response = await fetch('/api/v1/scientific/import-selection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_name: t('scientific.defaultProject'),
          results: selectedResults,
        }),
      })
      const data = (await response.json()) as { imported_count?: number; detail?: string }
      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`)
      }
      setImportMessage(
        t('scientific.importSuccess', { count: data.imported_count ?? selectedResults.length }),
      )
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : t('scientific.errors.import'),
      )
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <Stack spacing={2}>
      {errorMessage ? <Alert severity="warning">{errorMessage}</Alert> : null}
      {importMessage ? <Alert severity="success">{importMessage}</Alert> : null}

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, lg: 5 }}>
          <Paper sx={{ p: 2.5 }}>
            <Stack spacing={2}>
              <Typography variant="h6">{t('scientific.formTitle')}</Typography>

              <FormControl fullWidth size="small">
                <InputLabel id="scientific-source-label">
                  {t('scientific.fields.source')}
                </InputLabel>
                <Select
                  labelId="scientific-source-label"
                  value={form.source}
                  label={t('scientific.fields.source')}
                  disabled={isLoadingSources}
                  onChange={(event) =>
                    handleSourceChange(event.target.value as ScientificSourceKey)
                  }
                >
                  {sources.map((source) => (
                    <MenuItem key={source.key} value={source.key}>
                      {source.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                label={t('scientific.fields.query')}
                value={form.query}
                size="small"
                onChange={(event) =>
                  setForm((current) => ({ ...current, query: event.target.value }))
                }
              />

              <Grid container spacing={1.5}>
                <Grid size={{ xs: 12, sm: 5 }}>
                  <FormControl fullWidth size="small" disabled={!activeSource?.supported_identifiers.length}>
                    <InputLabel id="scientific-identifier-type-label">
                      {t('scientific.fields.identifierType')}
                    </InputLabel>
                    <Select
                      labelId="scientific-identifier-type-label"
                      value={form.identifierType}
                      label={t('scientific.fields.identifierType')}
                      onChange={(event) =>
                        setForm((current) => ({
                          ...current,
                          identifierType: event.target.value as IdentifierType | '',
                        }))
                      }
                    >
                      <MenuItem value="">{t('scientific.anyOption')}</MenuItem>
                      {(activeSource?.supported_identifiers ?? []).map((identifier) => (
                        <MenuItem key={identifier} value={identifier}>
                          {identifier.toUpperCase()}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid size={{ xs: 12, sm: 7 }}>
                  <TextField
                    fullWidth
                    size="small"
                    label={t('scientific.fields.identifier')}
                    value={form.identifier}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, identifier: event.target.value }))
                    }
                  />
                </Grid>
              </Grid>

              <Grid container spacing={1.5}>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    size="small"
                    type="date"
                    label={t('scientific.fields.startDate')}
                    value={form.startDate}
                    disabled={!activeSource?.supports_date_range}
                    InputLabelProps={{ shrink: true }}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, startDate: event.target.value }))
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    size="small"
                    type="date"
                    label={t('scientific.fields.endDate')}
                    value={form.endDate}
                    disabled={!activeSource?.supports_date_range}
                    InputLabelProps={{ shrink: true }}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, endDate: event.target.value }))
                    }
                  />
                </Grid>
              </Grid>

              <Grid container spacing={1.5}>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    size="small"
                    type="number"
                    label={t('scientific.fields.maxResults')}
                    value={form.maxResults}
                    inputProps={{
                      min: 1,
                      max: activeSource?.max_results_limit ?? 50,
                    }}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        maxResults: Number(event.target.value || 10),
                      }))
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    fullWidth
                    size="small"
                    label={t('scientific.fields.language')}
                    value={form.language}
                    disabled={!activeSource?.supports_language}
                    placeholder="en / fr"
                    onChange={(event) =>
                      setForm((current) => ({ ...current, language: event.target.value }))
                    }
                  />
                </Grid>
              </Grid>

              <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                <Button
                  variant="contained"
                  startIcon={<SearchOutlinedIcon />}
                  disabled={isSearching || isLoadingSources}
                  onClick={handleSearch}
                >
                  {isSearching ? t('scientific.searching') : t('scientific.search')}
                </Button>
                {activeSource ? (
                  <Chip
                    variant="outlined"
                    label={`${activeSource.label} | ${activeSource.official_api_url}`}
                  />
                ) : null}
              </Stack>
            </Stack>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, lg: 7 }}>
          <Paper sx={{ p: 2.5, height: '100%' }}>
            <Stack spacing={1.5}>
              <Stack
                direction={{ xs: 'column', md: 'row' }}
                justifyContent="space-between"
                alignItems={{ xs: 'flex-start', md: 'center' }}
                spacing={1}
              >
                <Box>
                  <Typography variant="h6">{t('scientific.resultsTitle')}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('scientific.resultsSummary', {
                      count: results.length,
                      selected: selectedResults.length,
                    })}
                  </Typography>
                </Box>
                <Button
                  variant="outlined"
                  startIcon={<PlaylistAddCheckCircleOutlinedIcon />}
                  disabled={!selectedResults.length || isImporting}
                  onClick={handleImport}
                >
                  {isImporting ? t('scientific.importing') : t('scientific.import')}
                </Button>
              </Stack>

              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={allSelected}
                        indeterminate={
                          selectedKeys.length > 0 && selectedKeys.length < results.length
                        }
                        onChange={(_, checked) => {
                          setSelectedKeys(checked ? results.map(resultKey) : [])
                        }}
                      />
                    </TableCell>
                    <TableCell>{t('scientific.columns.title')}</TableCell>
                    <TableCell>{t('scientific.columns.authors')}</TableCell>
                    <TableCell>{t('scientific.columns.date')}</TableCell>
                    <TableCell>{t('scientific.columns.source')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.map((result) => {
                    const key = resultKey(result)
                    const checked = selectedKeys.includes(key)
                    return (
                      <TableRow
                        key={key}
                        hover
                        selected={activeKey === key}
                        sx={{ cursor: 'pointer' }}
                        onClick={() => setActiveKey(key)}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={checked}
                            onChange={(_, nextChecked) => {
                              setSelectedKeys((current) =>
                                nextChecked
                                  ? [...current, key]
                                  : current.filter((item) => item !== key),
                              )
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ minWidth: 240 }}>
                          <Typography variant="body2" fontWeight={600}>
                            {result.title}
                          </Typography>
                          {result.journal ? (
                            <Typography variant="caption" color="text.secondary">
                              {result.journal}
                            </Typography>
                          ) : null}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {result.authors.slice(0, 3).join(', ') || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell>{result.publication_date || '-'}</TableCell>
                        <TableCell>
                          <Chip size="small" label={result.source} />
                        </TableCell>
                      </TableRow>
                    )
                  })}
                  {!results.length ? (
                    <TableRow>
                      <TableCell colSpan={5}>
                        <Typography variant="body2" color="text.secondary">
                          {t('scientific.emptyState')}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            </Stack>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2.5 }}>
        <Stack spacing={1.25}>
          <Typography variant="h6">{t('scientific.previewTitle')}</Typography>
          {activeResult ? (
            <>
              <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                <Chip size="small" label={activeResult.source} />
                {activeResult.document_type ? (
                  <Chip size="small" variant="outlined" label={activeResult.document_type} />
                ) : null}
              </Stack>
              <Typography variant="h5">{activeResult.title}</Typography>
              <Typography variant="body2" color="text.secondary">
                {activeResult.authors.join(', ') || '-'}
              </Typography>
              <Grid container spacing={1.5}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="body2">
                    <strong>{t('scientific.preview.date')}:</strong>{' '}
                    {activeResult.publication_date || '-'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>{t('scientific.preview.language')}:</strong>{' '}
                    {activeResult.language || '-'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>{t('scientific.preview.journal')}:</strong>{' '}
                    {activeResult.journal || '-'}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="body2">
                    <strong>DOI:</strong> {activeResult.doi || '-'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>PMID:</strong> {activeResult.pmid || '-'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>{t('scientific.preview.keyword')}:</strong>{' '}
                    {activeResult.keyword_used || '-'}
                  </Typography>
                </Grid>
              </Grid>
              <Typography variant="body2" color="text.secondary">
                {activeResult.abstract || t('scientific.noAbstract')}
              </Typography>
              <Box>
                <Link href={activeResult.url} target="_blank" rel="noreferrer" underline="hover">
                  <Stack direction="row" spacing={0.5} alignItems="center">
                    <LaunchOutlinedIcon fontSize="inherit" />
                    <span>{t('scientific.openSource')}</span>
                  </Stack>
                </Link>
              </Box>
            </>
          ) : (
            <Typography variant="body2" color="text.secondary">
              {t('scientific.noPreview')}
            </Typography>
          )}
        </Stack>
      </Paper>
    </Stack>
  )
}
