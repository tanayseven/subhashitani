# Subhashitani — Claude context

Static site generator for Sanskrit shlokas and their translations.
Flask routes are frozen into plain HTML by Frozen-Flask; no server is needed at runtime.

## Key commands

```sh
mise install                     # install Python 3.13 + uv 0.11.11
uv sync                          # install Python dependencies
uv run serve                     # dev server at http://localhost:5000
uv run python -m cli validate    # validate all content files
uv run python -m cli build       # freeze into build/
```

## Architecture

| File | Role |
|---|---|
| `app.py` | Flask routes (`/`, `/shlokas/<slug>.html`, `/search.json`) + Frozen-Flask config |
| `shlokas.py` | Parses markdown frontmatter and body into `Shloka` Pydantic models |
| `cli.py` | `python -m cli validate` and `python -m cli build` entry points |
| `templates/` | Jinja2 templates: `base.html`, `index.html`, `shloka.html` |
| `static/` | `css/style.css`, `js/search.js`, fonts (`Sanskrit-2003.ttf`, `NotoSansDevanagari.ttf`), `favicon.svg` |
| `assets/` | Source assets (fonts, icons) — copied to `static/` manually, not served directly |
| `content/` | Source markdown files, any directory depth |
| `build/` | Frozen output — gitignored, synced to S3 on CI |

## Content format

Each shloka is one `.md` file with YAML frontmatter:

```markdown
---
slug: source-short-title     # required — unique, becomes the URL slug
title: "..."                 # required
source: "..."                # required
date: YYYY-MM-DD             # required
tags: [tag1, tag2]           # optional list
---

# Shloka

Sanskrit text...

— Optional citation line (e.g. — चाणक्य नीति)

## Translations

### Hindi

Translation...

### English

Translation...
```

`slug` is the only routing key — filename and directory are ignored.
Languages are detected dynamically from `### Heading` names; no hardcoded list.

Font rendering: Sanskrit shloka text uses Sanskrit 2003 (`static/Sanskrit-2003.ttf`). Hindi translation sections get Noto Sans Devanagari (`static/NotoSansDevanagari.ttf`) via a `data-lang="hindi"` attribute on the translation wrapper div — set automatically from the `### Hindi` heading.

## Validation rules (`cli validate`)

- Required frontmatter fields: `slug`, `title`, `source`, `date`
- `slug` must be unique across all files
- `tags` must be a list if present

## CI / deployment

`.github/workflows/ci.yml` runs validate → build → S3 sync on every push.
S3 deploy (`build/` → `s3://subhashitani.tanay.tech/`) runs on `main` only,
using AWS OIDC (role `github-actions-for-subhashitani`, account id from `secrets.AWS_ACCOUNT_ID`).

## Conventions

- Never add `Co-Authored-By: Claude` to commit messages.
- Do not commit the `build/` directory.
- Keep `slug` values kebab-case and human-readable.