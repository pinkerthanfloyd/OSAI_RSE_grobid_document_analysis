from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import requests


@dataclass(frozen=True)
class GrobidConfig:
    base_url: str = "http://localhost:8070"
    timeout_s: int = 180


class GrobidClient:
    """Client: PDF -> TEI XML via GROBID REST API."""

    def __init__(self, config: GrobidConfig):
        self.config = config

    def process_fulltext_pdf(self, pdf_path: Path) -> str:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        endpoint = f"{self.config.base_url.rstrip('/')}/api/processFulltextDocument"

        with pdf_path.open("rb") as f:
            files = {"input": (pdf_path.name, f, "application/pdf")}
            resp = requests.post(endpoint, files=files, timeout=self.config.timeout_s)

        if resp.status_code != 200:
            raise RuntimeError(
                f"GROBID failed for {pdf_path.name}: HTTP {resp.status_code}\n{resp.text[:500]}"
            )
        return resp.text

