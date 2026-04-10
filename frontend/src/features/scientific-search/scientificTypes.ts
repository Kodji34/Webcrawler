export type ScientificSourceKey = 'crossref' | 'openalex' | 'pubmed' | 'hal'
export type IdentifierType = 'doi' | 'pmid' | 'hal_id'
export type FullTextSourceKey =
  | 'europe_pmc'
  | 'elsevier_tdm'
  | 'hal'
  | 'openedition'
  | 'cairn'
  | 'erudit'
export type FullTextOutcome =
  | 'full_text_retrieved'
  | 'full_text_not_authorized'
  | 'metadata_only'
  | 'failed'
export type FullTextAccessMode =
  | 'open_access'
  | 'authenticated_api'
  | 'bibliographic_only'
  | 'not_authorized'
  | 'unknown'

export type ScientificSourceDescriptor = {
  key: ScientificSourceKey
  label: string
  description: string
  official_api_url: string
  supports_date_range: boolean
  supports_language: boolean
  supported_identifiers: IdentifierType[]
  max_results_limit: number
}

export type ScientificSearchResult = {
  source: ScientificSourceKey
  title: string
  authors: string[]
  publication_date: string | null
  url: string
  language: string | null
  document_type: string | null
  doi: string | null
  pmid: string | null
  abstract: string | null
  journal: string | null
  pdf_url?: string | null
  keyword_used: string
}

export type ScientificSearchResponse = {
  query_log_id: string
  source: ScientificSourceKey
  results: ScientificSearchResult[]
  total_results: number
}

export type ScientificImportedRecord = {
  import_id: string
  project_name: string
  imported_at: string
  source: ScientificSourceKey
  title: string
  doi: string | null
  pmid: string | null
  publication_date: string | null
  journal: string | null
  url: string
  keyword_used: string
  metadata: ScientificSearchResult
}

export type FullTextSourceDescriptor = {
  key: FullTextSourceKey
  label: string
  description: string
  official_url: string
  requires_authentication: boolean
  supports_full_text: boolean
  notes: string
}

export type FullTextAcquisitionItem = {
  item_id: string
  scientific_import_id: string
  source: FullTextSourceKey
  outcome: FullTextOutcome
  access_mode: FullTextAccessMode
  title: string
  doi: string | null
  pmid: string | null
  landing_url: string
  full_text_url: string | null
  license_name: string | null
  language: string | null
  journal: string | null
  text_content: string | null
  excerpt: string | null
  notes: string[]
  created_at: string
}
