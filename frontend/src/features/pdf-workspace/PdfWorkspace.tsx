import CloudDownloadOutlinedIcon from '@mui/icons-material/CloudDownloadOutlined'
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined'
import PreviewOutlinedIcon from '@mui/icons-material/PreviewOutlined'
import SaveOutlinedIcon from '@mui/icons-material/SaveOutlined'
import ScienceOutlinedIcon from '@mui/icons-material/ScienceOutlined'
import SettingsSuggestOutlinedIcon from '@mui/icons-material/SettingsSuggestOutlined'
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  FormControl,
  FormControlLabel,
  FormGroup,
  Grid,
  InputLabel,
  List,
  ListItem,
  ListItemText,
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
  PDFCleaningOptions,
  PDFDependencyStatus,
  PDFExtractResponse,
  PDFExtractionMode,
  PDFImportResponse,
  PDFItem,
  PDFItemsResponse,
  PDFPreviewResponse,
  PDFSaveSelectionResponse,
  ScientificImportedRecord,
} from './pdfTypes'

const emptyDependencies: PDFDependencyStatus = {
  pymupdf_available: false,
  pdfplumber_available: false,
  pytesseract_available: false,
  tesseract_available: false,
  ocrmypdf_available: false,
  messages: [],
}

const defaultCleaningOptions: PDFCleaningOptions = {
  generate_cleaned_text: false,
  remove_headers: false,
  remove_footers: false,
  remove_page_numbers: false,
  remove_bibliography: false,
  normalize_whitespace: false,
}

function mergeItems(current: PDFItem[], updates: PDFItem[]) {
  const index = new Map(current.map((item) => [item.id, item]))
  for (const item of updates) {
    index.set(item.id, item)
  }
  return Array.from(index.values()).sort((left, right) =>
    right.created_at.localeCompare(left.created_at),
  )
}

function directPdfUrl(record: ScientificImportedRecord) {
  const metadataUrl = record.metadata?.pdf_url ?? null
  if (metadataUrl) {
    return metadataUrl
  }
  return record.url.toLowerCase().endsWith('.pdf') ? record.url : null
}

export function PdfWorkspace() {
  const { t } = useTranslation()
  const [items, setItems] = useState<PDFItem[]>([])
  const [dependencies, setDependencies] = useState<PDFDependencyStatus>(emptyDependencies)
  const [scientificImports, setScientificImports] = useState<ScientificImportedRecord[]>([])
  const [localDirectory, setLocalDirectory] = useState('')
  const [remoteUrls, setRemoteUrls] = useState('')
  const [projectName, setProjectName] = useState(t('pdf.defaultProject'))
  const [language, setLanguage] = useState('')
  const [extractionMode, setExtractionMode] = useState<PDFExtractionMode>('auto')
  const [selectedItemIds, setSelectedItemIds] = useState<string[]>([])
  const [selectedScientificIds, setSelectedScientificIds] = useState<string[]>([])
  const [activeItemId, setActiveItemId] = useState<string | null>(null)
  const [cleaningOptions, setCleaningOptions] =
    useState<PDFCleaningOptions>(defaultCleaningOptions)
  const [isLoading, setIsLoading] = useState(true)
  const [isImportingLocal, setIsImportingLocal] = useState(false)
  const [isImportingUrls, setIsImportingUrls] = useState(false)
  const [isPreviewing, setIsPreviewing] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const loadWorkspace = async () => {
    setIsLoading(true)
    try {
      const [itemsResponse, scientificResponse] = await Promise.all([
        fetch('/api/v1/pdf/items'),
        fetch('/api/v1/scientific/imports'),
      ])
      const itemsPayload = (await itemsResponse.json()) as PDFItemsResponse
      const scientificPayload = scientificResponse.ok
        ? ((await scientificResponse.json()) as ScientificImportedRecord[])
        : []

      if (!itemsResponse.ok) {
        throw new Error(t('pdf.errors.load'))
      }

      startTransition(() => {
        setItems(itemsPayload.items)
        setDependencies(itemsPayload.dependency_status)
        setScientificImports(scientificPayload)
        setActiveItemId((current) => current ?? itemsPayload.items[0]?.id ?? null)
        setErrorMessage(null)
      })
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('pdf.errors.load'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadWorkspace()
  }, [])

  const activeItem = useMemo(
    () => items.find((item) => item.id === activeItemId) ?? items[0] ?? null,
    [activeItemId, items],
  )

  const scientificCandidates = useMemo(
    () => scientificImports.filter((record) => Boolean(directPdfUrl(record))),
    [scientificImports],
  )

  const allSelected =
    items.length > 0 && selectedItemIds.length > 0 && selectedItemIds.length === items.length

  const previewText = activeItem?.text_cleaned || activeItem?.text_raw || activeItem?.preview_excerpt

  const handleLocalImport = async () => {
    if (!localDirectory.trim()) {
      return
    }

    setIsImportingLocal(true)
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      const response = await fetch('/api/v1/pdf/import-local', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          directory_path: localDirectory.trim(),
          recursive: true,
          language: language.trim() || undefined,
        }),
      })
      const payload = (await response.json()) as PDFImportResponse | { detail?: string }
      if (!response.ok) {
        throw new Error('detail' in payload ? payload.detail : t('pdf.errors.importLocal'))
      }
      const data = payload as PDFImportResponse
      setItems((current) => mergeItems(current, data.items))
      setActiveItemId(data.items[0]?.id ?? activeItemId)
      setSuccessMessage(t('pdf.messages.localImported', { count: data.imported_count }))
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : t('pdf.errors.importLocal'),
      )
    } finally {
      setIsImportingLocal(false)
    }
  }

  const handleUrlImport = async (mode: 'remote' | 'linked') => {
    const entries =
      mode === 'remote'
        ? remoteUrls
            .split(/\r?\n/)
            .map((value) => value.trim())
            .filter(Boolean)
            .map((url) => ({ url }))
        : scientificCandidates
            .filter((record) => selectedScientificIds.includes(record.import_id))
            .map((record) => ({
              url: directPdfUrl(record),
              label: record.title,
              linked_record_title: record.title,
            }))
            .filter(
              (entry): entry is { url: string; label: string; linked_record_title: string } =>
                Boolean(entry.url),
            )

    if (!entries.length) {
      return
    }

    setIsImportingUrls(true)
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      const response = await fetch('/api/v1/pdf/import-urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entries,
          import_type: mode === 'linked' ? 'linked_scientific_result' : 'remote',
          language: language.trim() || undefined,
        }),
      })
      const payload = (await response.json()) as PDFImportResponse | { detail?: string }
      if (!response.ok) {
        throw new Error('detail' in payload ? payload.detail : t('pdf.errors.importUrls'))
      }
      const data = payload as PDFImportResponse
      setItems((current) => mergeItems(current, data.items))
      setActiveItemId(data.items[0]?.id ?? activeItemId)
      setSelectedScientificIds([])
      setSuccessMessage(t('pdf.messages.urlImported', { count: data.imported_count }))
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : t('pdf.errors.importUrls'),
      )
    } finally {
      setIsImportingUrls(false)
    }
  }

  const handlePreview = async (itemId: string) => {
    setIsPreviewing(true)
    setErrorMessage(null)
    try {
      const response = await fetch('/api/v1/pdf/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item_id: itemId,
          extraction_mode: extractionMode,
          language: language.trim() || undefined,
          cleaning_options: cleaningOptions,
        }),
      })
      const payload = (await response.json()) as PDFPreviewResponse | { detail?: string }
      if (!response.ok) {
        throw new Error('detail' in payload ? payload.detail : t('pdf.errors.preview'))
      }
      const data = payload as PDFPreviewResponse
      setItems((current) => mergeItems(current, [data.item]))
      setDependencies(data.dependency_status)
      setActiveItemId(data.item.id)
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('pdf.errors.preview'))
    } finally {
      setIsPreviewing(false)
    }
  }

  const handleExtract = async () => {
    if (!selectedItemIds.length) {
      return
    }

    setIsExtracting(true)
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      const response = await fetch('/api/v1/pdf/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item_ids: selectedItemIds,
          extraction_mode: extractionMode,
          language: language.trim() || undefined,
          cleaning_options: cleaningOptions,
        }),
      })
      const payload = (await response.json()) as PDFExtractResponse | { detail?: string }
      if (!response.ok) {
        throw new Error('detail' in payload ? payload.detail : t('pdf.errors.extract'))
      }
      const data = payload as PDFExtractResponse
      setItems((current) => mergeItems(current, data.items))
      setDependencies(data.dependency_status)
      setActiveItemId(data.items[0]?.id ?? activeItemId)
      setSuccessMessage(t('pdf.messages.extracted', { count: data.items.length }))
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('pdf.errors.extract'))
    } finally {
      setIsExtracting(false)
    }
  }

  const handleSave = async () => {
    if (!selectedItemIds.length) {
      return
    }

    setIsSaving(true)
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      const response = await fetch('/api/v1/pdf/save-selection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: projectName.trim() || t('pdf.defaultProject'),
          item_ids: selectedItemIds,
        }),
      })
      const payload = (await response.json()) as PDFSaveSelectionResponse | { detail?: string }
      if (!response.ok) {
        throw new Error('detail' in payload ? payload.detail : t('pdf.errors.save'))
      }
      const data = payload as PDFSaveSelectionResponse
      await loadWorkspace()
      setSuccessMessage(t('pdf.messages.saved', { count: data.saved_count }))
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('pdf.errors.save'))
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Stack spacing={2}>
      {dependencies.messages.length ? (
        <Alert severity="info">{t('pdf.dependencyMessage')}</Alert>
      ) : null}
      {errorMessage ? <Alert severity="warning">{errorMessage}</Alert> : null}
      {successMessage ? <Alert severity="success">{successMessage}</Alert> : null}

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, xl: 4 }}>
          <Stack spacing={2}>
            <Paper sx={{ p: 2.25 }}>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <PictureAsPdfOutlinedIcon color="primary" />
                  <Typography variant="h6">{t('pdf.importLocalTitle')}</Typography>
                </Stack>
                <TextField
                  fullWidth
                  size="small"
                  label={t('pdf.fields.localDirectory')}
                  value={localDirectory}
                  onChange={(event) => setLocalDirectory(event.target.value)}
                />
                <TextField
                  fullWidth
                  size="small"
                  label={t('pdf.fields.language')}
                  placeholder="en / fr"
                  value={language}
                  onChange={(event) => setLanguage(event.target.value)}
                />
                <Button
                  variant="contained"
                  startIcon={<PictureAsPdfOutlinedIcon />}
                  disabled={isImportingLocal || isLoading}
                  onClick={handleLocalImport}
                >
                  {isImportingLocal ? t('pdf.loading') : t('pdf.importLocal')}
                </Button>
              </Stack>
            </Paper>

            <Paper sx={{ p: 2.25 }}>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <CloudDownloadOutlinedIcon color="primary" />
                  <Typography variant="h6">{t('pdf.importUrlsTitle')}</Typography>
                </Stack>
                <TextField
                  fullWidth
                  multiline
                  minRows={4}
                  size="small"
                  label={t('pdf.fields.urlList')}
                  value={remoteUrls}
                  onChange={(event) => setRemoteUrls(event.target.value)}
                />
                <Button
                  variant="outlined"
                  startIcon={<CloudDownloadOutlinedIcon />}
                  disabled={isImportingUrls || isLoading}
                  onClick={() => void handleUrlImport('remote')}
                >
                  {isImportingUrls ? t('pdf.loading') : t('pdf.importUrls')}
                </Button>
              </Stack>
            </Paper>

            <Paper sx={{ p: 2.25 }}>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <ScienceOutlinedIcon color="primary" />
                  <Typography variant="h6">{t('pdf.linkedTitle')}</Typography>
                </Stack>
                {scientificCandidates.length ? (
                  <>
                    <List sx={{ p: 0 }}>
                      {scientificCandidates.map((record) => (
                        <ListItem key={record.import_id} sx={{ px: 0 }}>
                          <Checkbox
                            checked={selectedScientificIds.includes(record.import_id)}
                            onChange={(_, checked) =>
                              setSelectedScientificIds((current) =>
                                checked
                                  ? [...current, record.import_id]
                                  : current.filter((item) => item !== record.import_id),
                              )
                            }
                          />
                          <ListItemText
                            primary={record.title}
                            secondary={directPdfUrl(record)}
                          />
                        </ListItem>
                      ))}
                    </List>
                    <Button
                      variant="outlined"
                      startIcon={<ScienceOutlinedIcon />}
                      disabled={!selectedScientificIds.length || isImportingUrls}
                      onClick={() => void handleUrlImport('linked')}
                    >
                      {t('pdf.importLinked')}
                    </Button>
                  </>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    {t('pdf.noLinked')}
                  </Typography>
                )}
              </Stack>
            </Paper>

            <Paper sx={{ p: 2.25 }}>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <SettingsSuggestOutlinedIcon color="primary" />
                  <Typography variant="h6">{t('pdf.processingTitle')}</Typography>
                </Stack>
                <FormControl fullWidth size="small">
                  <InputLabel id="pdf-mode-label">{t('pdf.fields.mode')}</InputLabel>
                  <Select
                    labelId="pdf-mode-label"
                    label={t('pdf.fields.mode')}
                    value={extractionMode}
                    onChange={(event) =>
                      setExtractionMode(event.target.value as PDFExtractionMode)
                    }
                  >
                    <MenuItem value="auto">{t('pdf.modes.auto')}</MenuItem>
                    <MenuItem value="native">{t('pdf.modes.native')}</MenuItem>
                    <MenuItem value="ocr">{t('pdf.modes.ocr')}</MenuItem>
                  </Select>
                </FormControl>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={cleaningOptions.generate_cleaned_text}
                        onChange={(event) =>
                          setCleaningOptions((current) => ({
                            ...current,
                            generate_cleaned_text: event.target.checked,
                          }))
                        }
                      />
                    }
                    label={t('pdf.cleaning.generate')}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={cleaningOptions.remove_headers}
                        onChange={(event) =>
                          setCleaningOptions((current) => ({
                            ...current,
                            remove_headers: event.target.checked,
                          }))
                        }
                      />
                    }
                    label={t('pdf.cleaning.headers')}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={cleaningOptions.remove_footers}
                        onChange={(event) =>
                          setCleaningOptions((current) => ({
                            ...current,
                            remove_footers: event.target.checked,
                          }))
                        }
                      />
                    }
                    label={t('pdf.cleaning.footers')}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={cleaningOptions.remove_page_numbers}
                        onChange={(event) =>
                          setCleaningOptions((current) => ({
                            ...current,
                            remove_page_numbers: event.target.checked,
                          }))
                        }
                      />
                    }
                    label={t('pdf.cleaning.pageNumbers')}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={cleaningOptions.remove_bibliography}
                        onChange={(event) =>
                          setCleaningOptions((current) => ({
                            ...current,
                            remove_bibliography: event.target.checked,
                          }))
                        }
                      />
                    }
                    label={t('pdf.cleaning.bibliography')}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={cleaningOptions.normalize_whitespace}
                        onChange={(event) =>
                          setCleaningOptions((current) => ({
                            ...current,
                            normalize_whitespace: event.target.checked,
                          }))
                        }
                      />
                    }
                    label={t('pdf.cleaning.whitespace')}
                  />
                </FormGroup>
                <TextField
                  fullWidth
                  size="small"
                  label={t('pdf.fields.projectName')}
                  value={projectName}
                  onChange={(event) => setProjectName(event.target.value)}
                />
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  <Button
                    variant="contained"
                    disabled={!selectedItemIds.length || isExtracting}
                    onClick={handleExtract}
                  >
                    {isExtracting ? t('pdf.processing') : t('pdf.extract')}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<SaveOutlinedIcon />}
                    disabled={!selectedItemIds.length || isSaving}
                    onClick={handleSave}
                  >
                    {isSaving ? t('pdf.saving') : t('pdf.save')}
                  </Button>
                </Stack>
              </Stack>
            </Paper>
          </Stack>
        </Grid>

        <Grid size={{ xs: 12, xl: 8 }}>
          <Stack spacing={2}>
            <Paper sx={{ p: 2.25 }}>
              <Stack spacing={1.5}>
                <Stack
                  direction={{ xs: 'column', md: 'row' }}
                  justifyContent="space-between"
                  alignItems={{ xs: 'flex-start', md: 'center' }}
                  spacing={1}
                >
                  <Box>
                    <Typography variant="h6">{t('pdf.resultsTitle')}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {t('pdf.resultsSummary', {
                        count: items.length,
                        selected: selectedItemIds.length,
                      })}
                    </Typography>
                  </Box>
                  <Chip
                    size="small"
                    color={dependencies.tesseract_available ? 'success' : 'warning'}
                    label={
                      dependencies.tesseract_available
                        ? t('pdf.dependencies.ready')
                        : t('pdf.dependencies.partial')
                    }
                  />
                </Stack>

                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={allSelected}
                          indeterminate={
                            selectedItemIds.length > 0 &&
                            selectedItemIds.length < items.length
                          }
                          onChange={(_, checked) =>
                            setSelectedItemIds(checked ? items.map((item) => item.id) : [])
                          }
                        />
                      </TableCell>
                      <TableCell>{t('pdf.columns.file')}</TableCell>
                      <TableCell>{t('pdf.columns.source')}</TableCell>
                      <TableCell>{t('pdf.columns.status')}</TableCell>
                      <TableCell>{t('pdf.columns.pages')}</TableCell>
                      <TableCell>{t('pdf.columns.mode')}</TableCell>
                      <TableCell>{t('pdf.columns.actions')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {items.map((item) => (
                      <TableRow
                        key={item.id}
                        hover
                        selected={item.id === activeItemId}
                        onClick={() => setActiveItemId(item.id)}
                        sx={{ cursor: 'pointer' }}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedItemIds.includes(item.id)}
                            onChange={(_, checked) =>
                              setSelectedItemIds((current) =>
                                checked
                                  ? [...current, item.id]
                                  : current.filter((entry) => entry !== item.id),
                              )
                            }
                          />
                        </TableCell>
                        <TableCell sx={{ minWidth: 260 }}>
                          <Typography variant="body2" fontWeight={600}>
                            {item.title || item.file_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {item.linked_record_title || item.original_path || item.original_url}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip size="small" label={item.source} />
                        </TableCell>
                        <TableCell>{item.extraction_status}</TableCell>
                        <TableCell>{item.page_count ?? '-'}</TableCell>
                        <TableCell>{item.used_extraction_mode || item.extraction_mode}</TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            startIcon={<PreviewOutlinedIcon />}
                            disabled={isPreviewing}
                            onClick={(event) => {
                              event.stopPropagation()
                              void handlePreview(item.id)
                            }}
                          >
                            {t('pdf.preview')}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                    {!items.length ? (
                      <TableRow>
                        <TableCell colSpan={7}>
                          <Typography variant="body2" color="text.secondary">
                            {isLoading ? t('pdf.loading') : t('pdf.empty')}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : null}
                  </TableBody>
                </Table>
              </Stack>
            </Paper>

            <Paper sx={{ p: 2.25 }}>
              <Stack spacing={1.5}>
                <Typography variant="h6">{t('pdf.previewTitle')}</Typography>
                {activeItem ? (
                  <>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      <Chip size="small" label={activeItem.source} />
                      <Chip
                        size="small"
                        variant="outlined"
                        label={`${t('pdf.fields.mode')}: ${
                          activeItem.used_extraction_mode || activeItem.extraction_mode
                        }`}
                      />
                      {activeItem.ocr_recommended ? (
                        <Chip size="small" color="warning" label={t('pdf.ocrRecommended')} />
                      ) : null}
                    </Stack>
                    <Typography variant="h6">{activeItem.title || activeItem.file_name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {activeItem.author || '-'}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        fontFamily: '"IBM Plex Mono", monospace',
                        bgcolor: 'rgba(29, 111, 214, 0.04)',
                        p: 1.5,
                        borderRadius: 2,
                        maxHeight: 420,
                        overflow: 'auto',
                      }}
                    >
                      {previewText || t('pdf.noPreview')}
                    </Typography>
                    {activeItem.heuristic_notes.length ? (
                      <Alert severity="info">
                        {activeItem.heuristic_notes.join(' ')}
                      </Alert>
                    ) : null}
                  </>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    {t('pdf.noPreview')}
                  </Typography>
                )}
              </Stack>
            </Paper>
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  )
}
