export type CorpusSourceType = 'pdf' | 'fulltext' | 'web'

export type CorpusSourceItem = {
  source_item_id: string
  source_type: CorpusSourceType
  title: string
  source_label: string | null
  language: string | null
  url: string | null
  has_text: boolean
  text_excerpt: string | null
  notes: string[]
}

export type CorpusStats = {
  document_count: number
  word_count: number
  character_count: number
  source_types: Record<string, number>
  languages: Record<string, number>
}

export type CorpusRecord = {
  corpus_id: string
  title: string
  description: string | null
  created_at: string
  stats: CorpusStats
  documents: Array<{
    source_item_id: string
    source_type: CorpusSourceType
    title: string
    language: string | null
    url: string | null
    text_content: string
  }>
}
