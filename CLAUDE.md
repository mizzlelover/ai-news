# Private Intelligence Observatory Claude Code Notes

Before changing this project, read:

- `NOTICE.md`
- `docs/PROJECT_SCOPE_AND_ATTRIBUTION.md`
- `skills/domain-intelligence-bootstrap/SKILL.md`
- `docs/DOMAIN_INTELLIGENCE_V0_1.md`
- `README.md`

Do not commit private OPML files, API keys, cookies, browser exports, or `.env`
values. Keep the public repo usable without secrets.

The product direction is methodology-first:

- Core layer: domain seed and map, optional decision context, intelligence
  requirements, EIE coverage denominator, expert attention reconstruction,
  point-in-time replay, source portfolio, coverage audit, and domain-ranked
  daily brief.
- Boundary layer: source adapters, delivery channels, and the Private Intelligence
  Observatory demo. The old AI News Radar reader interface is no longer shipped.

`skills/ai-news-radar/`, `skills/radar/`, the existing AI/文旅 fetch pipeline,
and its data are not the core method of this project. They are retained only as
historical or experimental engineering references and must be described as
based on LearnPrompt/ai-news-radar, with its MIT and LearnPrompt copyright notice
preserved. The old reader page and its page-specific assets are removed.

When adding a new domain, start from a domain seed and establish its map before
declaring a focused decision context, PIR, EIE, source role, availability time,
and audit output. Prefer stable public sources at the boundary.
