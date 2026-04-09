export type ScientificSourceKey = 'crossref' | 'openalex' | 'pubmed' | 'hal'
export type IdentifierType = 'doi' | 'pmid' | 'hal_id'

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
  keyword_used: string
}

export type ScientificSearchResponse = {
  query_log_id: string
  source: ScientificSourceKey
  results: ScientificSearchResult[]
  total_results: number
}
