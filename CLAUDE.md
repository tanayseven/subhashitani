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
| `shlokas.py` | Parses markdown frontmatter and body into `Shloka` dataclasses |
| `cli.py` | `python -m cli validate` and `python -m cli build` entry points |
| `templates/` | Jinja2 templates: `base.html`, `index.html`, `shloka.html` |
| `static/` | `css/style.css`, `js/search.js` (client-side search over `search.json`) |
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

## Translations

### English

Translation...

### Hindi

Translation...
```

`slug` is the only routing key — filename and directory are ignored.
Languages are detected dynamically from `### Heading` names; no hardcoded list.

## Validation rules (`cli validate`)

- Required frontmatter fields: `slug`, `title`, `source`, `date`
- `slug` must be unique across all files
- `tags` must be a list if present

## CI / deployment

`.github/workflows/ci.yml` runs validate → build → S3 sync on every push.
S3 deploy (`build/` → `s3://projects.tanay.tech/subhashitani/`) runs on `main` only,
using AWS OIDC (role `subhahitani`, account id from `secrets.AWS_ACCOUNT_ID`).

## Conventions

- Never add `Co-Authored-By: Claude` to commit messages.
- Do not commit the `build/` directory.
- Keep `slug` values kebab-case and human-readable.