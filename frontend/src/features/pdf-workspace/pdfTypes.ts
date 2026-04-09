export type PDFSource = 'local_files' | 'remote_pdf' | 'linked_scientific_result'
export type PDFImportType = 'local' | 'remote' | 'linked_scientific_result'
export type PDFExtractionMode = 'native' | 'ocr' | 'auto'
export type PDFExtractionStatus = 'imported' | 'ready' | 'saved' | 'failed' | 'dependency_missing'

export type PDFCleaningOptions = {
  generate_cleaned_text: boolean
  remove_headers: boolean
  remove_footers: boolean
  remove_page_numbers: boolean
  remove_bibliography: boolean
  normalize_whitespace: boolean
}

export type PDFItem = {
  id: string
  source: PDFSource
  file_name: string
  original_path: string | null
  original_url: string | null
  storage_path: string
  import_type: PDFImportType
  language: string | null
  extraction_mode: PDFExtractionMode
  used_extraction_mode: PDFExtractionMode | null
  extraction_status: PDFExtractionStatus
  page_count: number | null
  title: string | null
  author: string | null
  text_raw: string | null
  text_cleaned: string | null
  has_ocr: boolean
  ocr_recommended: boolean
  dependency_messages: string[]
  heuristic_notes: string[]
  linked_record_title: string | null
  saved_to_project: boolean
  project_name: string | null
  created_at: string
  preview_excerpt: string | null
}

export type PDFDependencyStatus = {
  pymupdf_available: boolean
  pdfplumber_available: boolean
  pytesseract_available: boolean
  tesseract_available: boolean
  ocrmypdf_available: boolean
  messages: string[]
}

export type PDFItemsResponse = {
  items: PDFItem[]
  dependency_status: PDFDependencyStatus
}

export type PDFImportResponse = {
  imported_count: number
  items: PDFItem[]
}

export type PDFJob = {
  job_id: string
  created_at: string
  completed_at: string | null
  item_ids: string[]
  extraction_mode: PDFExtractionMode
  status: PDFExtractionStatus
  processed_count: number
  warnings: string[]
}

export type PDFExtractResponse = {
  job: PDFJob
  items: PDFItem[]
  dependency_status: PDFDependencyStatus
}

export type PDFPreviewResponse = {
  item: PDFItem
  dependency_status: PDFDependencyStatus
}

export type PDFSaveSelectionResponse = {
  project_name: string
  saved_count: number
}

export type ScientificImportedRecord = {
  import_id: string
  project_name: string
  imported_at: string
  source: string
  title: string
  url: string
  metadata: {
    pdf_url?: string | null
  }
}
