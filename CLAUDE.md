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

- Core layer: decision context, intelligence requirements, EIE coverage denominator,
  expert attention reconstruction, point-in-time replay, source portfolio,
  coverage audit, and domain-ranked daily brief.
- Boundary layer: source adapters, delivery channels, static pages, and optional
  AI News Radar compatibility components.

`skills/ai-news-radar/`, `skills/radar/`, the existing AI/文旅 fetch pipeline,
and its static page are not the core method of this project. They are retained
for reuse and must be described as based on LearnPrompt/ai-news-radar, with its
MIT and LearnPrompt copyright notice preserved.

When adding a new domain, start from the core Bundle and declare the decision
context, PIR, EIE, source role, availability time, and audit output before
choosing a collection adapter. Prefer stable public sources at the boundary.
