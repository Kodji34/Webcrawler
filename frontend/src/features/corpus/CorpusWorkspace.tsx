import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined'
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  Grid,
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

import type { CorpusRecord, CorpusSourceItem } from './corpusTypes'

export function CorpusWorkspace() {
  const { t } = useTranslation()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [sources, setSources] = useState<CorpusSourceItem[]>([])
  const [corpora, setCorpora] = useState<CorpusRecord[]>([])
  const [selectedSourceIds, setSelectedSourceIds] = useState<string[]>([])
  const [activeCorpusId, setActiveCorpusId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const textSources = useMemo(() => sources.filter((source) => source.has_text), [sources])
  const activeCorpus = useMemo(
    () => corpora.find((corpus) => corpus.corpus_id === activeCorpusId) ?? corpora[0] ?? null,
    [activeCorpusId, corpora],
  )

  const loadData = async () => {
    setIsLoading(true)
    try {
      const [sourcesResponse, corporaResponse] = await Promise.all([
        fetch('/api/v1/corpus/sources'),
        fetch('/api/v1/corpus/items'),
      ])
      if (!sourcesResponse.ok || !corporaResponse.ok) {
        throw new Error('HTTP error')
      }
      const [sourcesPayload, corporaPayload] = await Promise.all([
        sourcesResponse.json() as Promise<{ items: CorpusSourceItem[] }>,
        corporaResponse.json() as Promise<{ corpora: CorpusRecord[] }>,
      ])
      startTransition(() => {
        setSources(sourcesPayload.items)
        setCorpora(corporaPayload.corpora)
        setActiveCorpusId((current) => current ?? corporaPayload.corpora[0]?.corpus_id ?? null)
        setErrorMessage(null)
      })
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('corpus.errors.load'))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadData()
  }, [])

  const handleCreate = async () => {
    if (!title.trim() || !selectedSourceIds.length) {
      return
    }

    setIsCreating(true)
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      const response = await fetch('/api/v1/corpus/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || undefined,
          source_item_ids: selectedSourceIds,
        }),
      })
      const payload = (await response.json()) as { corpus?: CorpusRecord; detail?: string }
      if (!response.ok || !payload.corpus) {
        throw new Error(payload.detail || `HTTP ${response.status}`)
      }
      setSuccessMessage(t('corpus.messages.created', { count: payload.corpus.stats.document_count }))
      setTitle('')
      setDescription('')
      setSelectedSourceIds([])
      await loadData()
      setActiveCorpusId(payload.corpus.corpus_id)
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : t('corpus.errors.create'))
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <Stack spacing={2}>
      {errorMessage ? <Alert severity="warning">{errorMessage}</Alert> : null}
      {successMessage ? <Alert severity="success">{successMessage}</Alert> : null}

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, lg: 5 }}>
          <Paper sx={{ p: 2.25 }}>
            <Stack spacing={1.5}>
              <Typography variant="h6">{t('corpus.builderTitle')}</Typography>
              <TextField
                label={t('corpus.fields.title')}
                value={title}
                size="small"
                onChange={(event) => setTitle(event.target.value)}
              />
              <TextField
                label={t('corpus.fields.description')}
                value={description}
                size="small"
                multiline
                minRows={3}
                onChange={(event) => setDescription(event.target.value)}
              />
              <Button
                variant="contained"
                startIcon={<Inventory2OutlinedIcon />}
                disabled={!title.trim() || !selectedSourceIds.length || isCreating}
                onClick={handleCreate}
              >
                {isCreating ? t('corpus.creating') : t('corpus.create')}
              </Button>
              <Typography variant="caption" color="text.secondary">
                {t('corpus.boundaryNote')}
              </Typography>
            </Stack>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, lg: 7 }}>
          <Paper sx={{ p: 2.25 }}>
            <Stack spacing={1.5}>
              <Box>
                <Typography variant="h6">{t('corpus.sourcesTitle')}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('corpus.sourcesSummary', {
                    count: textSources.length,
                    selected: selectedSourceIds.length,
                  })}
                </Typography>
              </Box>
              <TableContainer sx={{ maxHeight: 400, border: (theme) => `1px solid ${theme.palette.divider}`, borderRadius: 2 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox" />
                      <TableCell>{t('corpus.columns.title')}</TableCell>
                      <TableCell>{t('corpus.columns.type')}</TableCell>
                      <TableCell>{t('corpus.columns.language')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {textSources.map((source) => {
                      const checked = selectedSourceIds.includes(source.source_item_id)
                      return (
                        <TableRow key={source.source_item_id} hover>
                          <TableCell padding="checkbox">
                            <Checkbox
                              checked={checked}
                              onChange={(_, nextChecked) =>
                                setSelectedSourceIds((current) =>
                                  nextChecked
                                    ? [...current, source.source_item_id]
                                    : current.filter((item) => item !== source.source_item_id),
                                )
                              }
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight={600}>
                              {source.title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {source.text_excerpt || '-'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip size="small" label={source.source_type} />
                          </TableCell>
                          <TableCell>{source.language || '-'}</TableCell>
                        </TableRow>
                      )
                    })}
                    {!textSources.length ? (
                      <TableRow>
                        <TableCell colSpan={4}>
                          <Typography variant="body2" color="text.secondary">
                            {isLoading ? t('corpus.loading') : t('corpus.emptySources')}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : null}
                  </TableBody>
                </Table>
              </TableContainer>
            </Stack>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2.25 }}>
        <Stack spacing={1.5}>
          <Typography variant="h6">{t('corpus.corporaTitle')}</Typography>
          {activeCorpus ? (
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 5 }}>
                <Stack spacing={1}>
                  {corpora.map((corpus) => (
                    <Paper
                      key={corpus.corpus_id}
                      variant="outlined"
                      sx={{ p: 1.5, cursor: 'pointer' }}
                      onClick={() => setActiveCorpusId(corpus.corpus_id)}
                    >
                      <Typography variant="body2" fontWeight={700}>
                        {corpus.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {t('corpus.cardStats', {
                          docs: corpus.stats.document_count,
                          words: corpus.stats.word_count,
                        })}
                      </Typography>
                    </Paper>
                  ))}
                </Stack>
              </Grid>
              <Grid size={{ xs: 12, md: 7 }}>
                <Stack spacing={1}>
                  <Typography variant="h6">{activeCorpus.title}</Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    <Chip size="small" label={t('corpus.stats.documents', { count: activeCorpus.stats.document_count })} />
                    <Chip size="small" label={t('corpus.stats.words', { count: activeCorpus.stats.word_count })} />
                    <Chip size="small" label={t('corpus.stats.characters', { count: activeCorpus.stats.character_count })} />
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {activeCorpus.description || t('corpus.noDescription')}
                  </Typography>
                  <Link
                    href={`/api/v1/corpus/items/${activeCorpus.corpus_id}/export-text`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {t('corpus.exportText')}
                  </Link>
                </Stack>
              </Grid>
            </Grid>
          ) : (
            <Typography variant="body2" color="text.secondary">
              {isLoading ? t('corpus.loading') : t('corpus.emptyCorpora')}
            </Typography>
          )}
        </Stack>
      </Paper>
    </Stack>
  )
}
