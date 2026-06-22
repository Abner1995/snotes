# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal learning notes / knowledge base built with Sphinx, hosted on ReadTheDocs. Content is written in Chinese (Simplified) using MyST Markdown (`.md` files). The `lumache.py` at the repo root is a placeholder from a Sphinx tutorial — it is not the actual deliverable.

## Build & Preview

```bash
# Install dependencies
pip install -r docs/requirements.txt

# Build HTML
cd docs && make html

# The output lands in docs/build/html/
```

The live site is at: `https://snotes.readthedocs.io/zh-cn/latest/index.html`

## Architecture

```
docs/
  source/           # Sphinx source tree — all content lives here
    conf.py         # Sphinx config (sphinx_book_theme, MyST, extensions)
    index.md        # Root toctree — every top-level section must be linked here
    _static/        # Logos, custom CSS, JS
    images/         # All inline images organized by section (e.g., images/dotnet/...)
    dotnet/         # .NET notes (Clean Architecture, WebAPI, EF Core, microservices)
    docker/         # Docker notes
    fund/           # Fund investing notes
    stock/          # Stock/technical analysis notes
    git/            # Git usage notes
    Linux/          # Linux commands & server debugging (includes SSH docs)
    MySQL/          # MySQL notes
    PHP/            # PHP notes
    python/         # Python notes
    redis/          # Redis notes
    SSH/            # SSH key setup docs
    reference/blog/ # Ablog-based blog posts
    references.bib  # BibTeX references
  build/            # Generated output (gitignored, but committed in this repo)
  requirements.txt  # Python deps for building docs
```

## Key Conventions

- **Sphinx `conf.py`** (`docs/source/conf.py`): The Sphinx configuration. Theme is `sphinx_book_theme`, language is `zh-cn`. Extensions in use include `myst_nb` (MyST + Jupyter notebooks), `ablog`, `sphinx_design`, `sphinx_tabs`, `sphinx_copybutton`, `sphinx_thebe`, `sphinx_togglebutton`, and several others.
- **New content**: Add a `.md` file under the appropriate `docs/source/<section>/` directory, then add it to that section's `index.md` toctree (and to the root `index.md` toctree if it's a new top-level section).
- **Images**: Reference from `docs/source/images/`, following the section-based subdirectory convention.
- **The `lumache.py` package** at the repo root is a dummy Python package included by the Sphinx quickstart tutorial — it is not the actual project. The project's sole output is the Sphinx documentation site.
- **Build output**: `docs/build/` is committed to the repo (unusual, but useful for direct browsing). Regenerate with `cd docs && make html`.
