# Subhashitani

A static site generator for Sanskrit shlokas and their translations. Content is written in Markdown, built with Flask + Frozen-Flask into a deployable set of HTML pages with client-side search.

## Requirements

- [mise](https://mise.jdx.dev/) — manages Python and uv versions
- [uv](https://docs.astral.sh/uv/) — managed automatically by mise

## Setup

```sh
mise install
uv sync
```

## Development

```sh
uv run serve        # live Flask dev server at http://localhost:5000
```

## Adding a shloka

Create a `.md` file anywhere inside `content/` (filename and depth don't matter):

```markdown
---
slug: source-short-title          # unique identifier, used as the URL slug
title: "Short descriptive title"
source: "Source text name"
tags: [wisdom, conduct]
date: 2026-05-08
---

# Shloka

Sanskrit text goes here...

## Translations

### English

Translation goes here...

### Hindi

Translation goes here...
```

Any number of `### Language` sections are supported.

## Build

```sh
uv run python -m cli validate   # check all content files for errors
uv run python -m cli build      # freeze Flask app into build/
```

Output lands in `build/` and is gitignored.

## Deployment

CI runs on every push. On `main`, the `build/` folder is synced to S3:

```sh
aws s3 sync --delete build/ s3://projects.tanay.tech/subhashitani/
```

Authentication uses AWS OIDC — no stored credentials. See `.github/workflows/ci.yml`.

## Project structure

```
content/          markdown source files (any directory depth)
templates/        Jinja2 HTML templates
static/           CSS and JS copied as-is into build/
app.py            Flask routes + Frozen-Flask freeze
shlokas.py        content parser
cli.py            validate and build CLI (python -m cli)
build/            generated static site (gitignored)
```