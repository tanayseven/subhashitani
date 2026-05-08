import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import frontmatter
import markdown as md_lib


@dataclass
class Translation:
    language: str
    text: str
    html: str


@dataclass
class Shloka:
    slug: str
    title: str
    source: str
    tags: list[str]
    date: date
    shloka_text: str
    shloka_html: str
    translations: list[Translation]

    @property
    def translation_languages(self) -> list[str]:
        return [t.language for t in self.translations]


def _to_html(text: str) -> str:
    return md_lib.markdown(text)


def _parse_body(body: str) -> tuple[str, list[Translation]]:
    shloka_match = re.search(
        r"^#\s+Shloka\s*\n(.*?)(?=^##|\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    shloka_text = shloka_match.group(1).strip() if shloka_match else ""

    translations: list[Translation] = []
    trans_match = re.search(
        r"^##\s+Translations\s*\n(.*)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if trans_match:
        parts = re.split(r"^###\s+(.+)$", trans_match.group(1), flags=re.MULTILINE)
        # parts: ["", "Language1", "content1", "Language2", "content2", ...]
        for i in range(1, len(parts), 2):
            lang = parts[i].strip()
            text = parts[i + 1].strip() if i + 1 < len(parts) else ""
            translations.append(Translation(language=lang, text=text, html=_to_html(text)))

    return shloka_text, translations


def parse_shloka_file(path: Path) -> Shloka:
    post = frontmatter.load(str(path))
    meta: dict[str, Any] = post.metadata

    raw_date = meta.get("date", date.today())
    if isinstance(raw_date, str):
        raw_date = datetime.strptime(raw_date, "%Y-%m-%d").date()

    shloka_text, translations = _parse_body(post.content)

    return Shloka(
        slug=meta["slug"],
        title=meta.get("title", ""),
        source=meta.get("source", ""),
        tags=meta.get("tags", []),
        date=raw_date,
        shloka_text=shloka_text,
        shloka_html=_to_html(shloka_text),
        translations=translations,
    )


def load_all_shlokas() -> list[Shloka]:
    shlokas = [parse_shloka_file(p) for p in Path("content").rglob("*.md")]
    return sorted(shlokas, key=lambda s: s.date, reverse=True)