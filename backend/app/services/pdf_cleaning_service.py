from __future__ import annotations

import re
from collections import Counter

from backend.app.schemas.pdf import PDFCleaningOptions


class PDFCleaningService:
    def clean_text(
        self,
        page_texts: list[str],
        options: PDFCleaningOptions,
    ) -> tuple[str | None, list[str]]:
        if not options.generate_cleaned_text:
            return None, []

        notes: list[str] = []
        processed_pages = [self._split_lines(text) for text in page_texts]

        if options.remove_headers:
            processed_pages, header_notes = self._remove_repeated_edge_lines(
                processed_pages,
                edge="header",
            )
            notes.extend(header_notes)
        if options.remove_footers:
            processed_pages, footer_notes = self._remove_repeated_edge_lines(
                processed_pages,
                edge="footer",
            )
            notes.extend(footer_notes)
        if options.remove_page_numbers:
            processed_pages, page_number_notes = self._remove_page_numbers(processed_pages)
            notes.extend(page_number_notes)

        merged_text = "\n\n".join(
            "\n".join(lines).strip() for lines in processed_pages if any(lines)
        ).strip()

        if options.remove_bibliography:
            merged_text, bibliography_notes = self._remove_bibliography(merged_text)
            notes.extend(bibliography_notes)

        if options.normalize_whitespace:
            merged_text = self._normalize_whitespace(merged_text)
            notes.append("Whitespace normalization applied.")

        return merged_text or None, notes

    @staticmethod
    def _split_lines(text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _remove_repeated_edge_lines(
        self,
        pages: list[list[str]],
        *,
        edge: str,
    ) -> tuple[list[list[str]], list[str]]:
        candidates = []
        for lines in pages:
            if not lines:
                continue
            candidates.append(lines[0] if edge == "header" else lines[-1])

        if len(candidates) < 2:
            return pages, []

        counter = Counter(candidate for candidate in candidates if len(candidate) > 3)
        threshold = max(2, int(len(pages) * 0.6))
        repeated = {line for line, count in counter.items() if count >= threshold}
        if not repeated:
            return pages, []

        cleaned_pages: list[list[str]] = []
        for lines in pages:
            page_lines = list(lines)
            if page_lines:
                if edge == "header" and page_lines[0] in repeated:
                    page_lines = page_lines[1:]
                elif edge == "footer" and page_lines[-1] in repeated:
                    page_lines = page_lines[:-1]
            cleaned_pages.append(page_lines)

        note = (
            "Repeated headers removed using a frequency heuristic."
            if edge == "header"
            else "Repeated footers removed using a frequency heuristic."
        )
        return cleaned_pages, [note]

    @staticmethod
    def _remove_page_numbers(pages: list[list[str]]) -> tuple[list[list[str]], list[str]]:
        pattern = re.compile(
            r"^(page\s+)?(\d+|[ivxlcdm]+)(\s*/\s*(\d+|[ivxlcdm]+))?$",
            flags=re.IGNORECASE,
        )
        cleaned: list[list[str]] = []
        changed = False
        for lines in pages:
            filtered = [line for line in lines if not pattern.match(line.strip())]
            changed = changed or len(filtered) != len(lines)
            cleaned.append(filtered)
        notes = ["Standalone page numbers removed."] if changed else []
        return cleaned, notes

    @staticmethod
    def _remove_bibliography(text: str) -> tuple[str, list[str]]:
        pattern = re.compile(
            r"(^|\n)(references|bibliography|reference list|references cited|bibliographie|références)\s*\n",
            flags=re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            return text, []
        return text[: match.start()].strip(), [
            "Content after a references heading was removed using a simple heuristic.",
        ]

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        compact = re.sub(r"[ \t]+", " ", text)
        compact = re.sub(r"\n{3,}", "\n\n", compact)
        return compact.strip()
