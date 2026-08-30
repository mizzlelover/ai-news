# Private Intelligence Observatory Agent Notes

## Scope

This repo's primary product is Private Intelligence Observatory: a
domain-agnostic intelligence methodology and runtime covering decision context,
intelligence requirements, expert attention reconstruction, historical replay,
source portfolio, coverage audit, and daily brief delivery. The old AI News
Radar reader interface has been removed from the release surface. Early
collection scripts, data, and Scout/Bole Skills remain only as optional
historical or experimental engineering references.

## Working Rules

- Keep changes small and reviewable.
- Search the repo before changing source fetchers or output schemas.
- Do not commit private feeds, secrets, tokens, cookies, or `.env` values.
- Do not commit `feeds/follow.opml`; use `feeds/follow.example.opml` as the public template.
- Prefer stable public RSS/Atom/OPML sources before adding custom scrapers.
- Keep the core methodology visible: do not make AI-news collection or old
  reader assets the default project story.
- Preserve `NOTICE.md` and `docs/PROJECT_SCOPE_AND_ATTRIBUTION.md` when changing
  or redistributing retained upstream collection references.

## Source Strategy

Read `docs/SOURCE_COVERAGE.md` before adding or removing sources.

Default source priority:

1. Official RSS/Atom feeds and OPML collections.
2. Stable public JSON APIs or static pages with timestamps.
3. Curated newsletters or changelogs with public feeds.
4. Manual/custom adapters only when the source is high-signal and stable.

Avoid account-bound timelines, broad personal social feeds, login-gated pages,
and fragile bridges unless the user explicitly accepts the maintenance cost.

## Common Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m py_compile scripts/update_news.py
python -m pytest -q
python scripts/update_news.py --output-dir data --window-hours 24 --rss-opml feeds/follow.opml
python -m http.server 8080
```

For core agent workflows, read `skills/domain-intelligence-bootstrap/SKILL.md`.
Read `skills/ai-news-radar/SKILL.md` only when working on the retained historical
or experimental collection reference.
