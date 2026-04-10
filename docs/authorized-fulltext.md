# Authorized Full-Text Notes

This layer is intentionally compliance-first.

## Supported access paths

- Europe PMC / PMC: open access full text through the official Europe PMC API when `fullTextXML` is exposed
- Elsevier / ScienceDirect: official TDM API with `ELSEVIER_API_KEY` and optional `ELSEVIER_INSTTOKEN`
- HAL: repository metadata plus directly accessible deposited files
- OpenEdition Journals: metadata via OAI, and HTML retrieval only for clearly accessible article pages
- Cairn: bibliographic handling only
- Erudit: HTML retrieval only when the page is openly accessible without bypassing restrictions

## Outcomes

- `full_text_retrieved`
- `full_text_not_authorized`
- `metadata_only`
- `failed`

## Important limits

- no paywall bypassing
- no unofficial scraping
- no credential reuse beyond official API settings
- OpenEdition and Erudit body extraction is heuristic and may fall back to metadata-only even when a page is reachable
