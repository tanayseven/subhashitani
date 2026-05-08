import re
from datetime import date
from pathlib import Path
from typing import Any

import frontmatter
import markdown as md_lib
from pydantic import BaseModel, computed_field, model_validator


class Translation(BaseModel):
    language: str
    text: str
    html: str


class Shloka(BaseModel):
    slug: str
    title: str
    source: str
    tags: list[str]
    date: date
    shloka_text: str
    shloka_html: str
    translations: list[Translation]

    @computed_field
    @property
    def translation_languages(self) -> list[str]:
        return [t.language for t in self.translations]

    @model_validator(mode="before")
    @classmethod
    def coerce_tags(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get("tags") is None:
            data["tags"] = []
        return data


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

    shloka_text, translations = _parse_body(post.content)

    return Shloka(
        slug=meta["slug"],
        title=meta.get("title", ""),
        source=meta.get("source", ""),
        tags=meta.get("tags"),
        date=meta.get("date", date.today()),
        shloka_text=shloka_text,
        shloka_html=_to_html(shloka_text),
        translations=translations,
    )


def load_all_shlokas() -> list[Shloka]:
    shlokas = [parse_shloka_file(p) for p in Path("content").rglob("*.md")]
    return sorted(shlokas, key=lambda s: s.date, reverse=True)
