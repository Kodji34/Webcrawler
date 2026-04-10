export type WebImportStatus = 'text_retrieved' | 'metadata_only' | 'not_authorized' | 'failed'

export type WebImportedArticle = {
  item_id: string
  project_name: string
  url: string
  label: string | null
  title: string | null
  description: string | null
  language: string | null
  source_domain: string | null
  status: WebImportStatus
  text_content: string | null
  excerpt: string | null
  content_type: string | null
  imported_at: string
  notes: string[]
}
