# Private Intelligence Observatory

## Domain Intelligence Methodology and Briefing System

**Help professionals in any domain build an auditable, continuously maintained intelligence practice with AI.**

[![Private Intelligence Observatory CI](https://github.com/mizzlelover/private-intelligence-observatory/actions/workflows/domain-intelligence.yml/badge.svg)](https://github.com/mizzlelover/private-intelligence-observatory/actions/workflows/domain-intelligence.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[Try the demo](https://mizzlelover.github.io/private-intelligence-observatory/demo/) · [Practitioner guide](docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md) · [Core methodology](docs/DOMAIN_INTELLIGENCE_V0_1.md) · [Engine](packages/domain-intelligence/README.md) · [Scope and attribution](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md) · [中文](README.md)

---

## This is not another AI news reader

Most AI assistants, daily briefings, and knowledge engines are built around AI practitioners tracking AI. Professionals in tourism, manufacturing, education, agriculture, healthcare, energy, city building, and other domains also need to track policy, projects, technology, competition, supply chains, and markets. Very few tools help them turn that need into a durable operating system.

The people who need this capability often do not work with RSS, crawlers, prompts, databases, or GitHub workflows. They may not even know which professional question to ask when they first enter a field. Private Intelligence Observatory closes that gap: start with one domain keyword, let the system build the map, people, sources, and knowledge engine, then turn a chosen question into a maintainable process for collection, verification, interpretation, delivery, and improvement.

A daily brief, web page, or notification is only a delivery format. The product is the method: what to ask, who is likely to know first, which sources have proved useful, what remains uncovered, and how evidence supports the next decision.

## Core methodology

~~~text
Domain seed
→ Domain map / vocabulary / participants
→ Decision context
→ Intelligence Requirement Graph
→ Essential Information Elements
→ Expert Attention Reconstruction
→ Point-in-time Source Benchmark
→ Source Portfolio
→ Coverage Audit
→ Domain-ranked Daily Brief
→ Focused watch / human feedback
~~~

The system first turns “I only know this domain” into a durable field map, then into auditable questions:

- What are this domain's boundaries, participants, vocabulary, and operating chains?
- Which people, organizations, projects, and artifacts define or change it?
- Which information elements must remain visible, and which sources cover confirmation, interpretation, discovery, and frontline feedback?
- Once I have a specific decision, which requirements and information elements should become a focused watch?
- Which experts, institutions, artifacts, and events expose early signals?
- Was a source actually available at the time, and has it proved useful historically?
- What does the current portfolio cover, and what remains unknown?
- Does the brief preserve evidence, timing, and a path for further checking?

The same engine can support robotics, data assets, tourism, cybersecurity, education, agriculture, or a new domain. Each domain starts from its own seed and map, then develops decision context and information requirements rather than copying AI-news categories and thresholds.

## Start from the audience you are serving

### If you work in a professional domain

Open the [demo](https://mizzlelover.github.io/private-intelligence-observatory/demo/) and enter a domain keyword such as “digital tourism”. See how the system builds the map before asking you to choose a focused question. Then read the [practitioner guide](docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md) and use the [core methodology](docs/DOMAIN_INTELLIGENCE_V0_1.md) to define the domain, source roles, and, when needed, your first PIRs and EIEs.

You do not need to become an engineer first, or arrive with a polished professional question. Bring the domain; Private Intelligence Observatory turns it into a durable intelligence mechanism.

### If you are an engineering collaborator

Start with the [engine](packages/domain-intelligence/README.md) and the [Bootstrap Skill](skills/domain-intelligence-bootstrap/SKILL.md). The engine handles EAR, point-in-time replay, source portfolios, coverage audits, and domain-ranked briefs. Collection, databases, email, delivery, and web presentation remain replaceable boundary adapters.

Minimal runnable example:

~~~bash
uv run --project packages/domain-intelligence dib \
  packages/domain-intelligence/examples/data-elements.json \
  --output-dir out/domain-intelligence
~~~

## Repository map

| Path | Purpose |
| --- | --- |
| demo/ | Audience-facing product demo, domain-first entry, and methodology visuals |
| docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md | Application guide for non-technical users |
| docs/DOMAIN_INTELLIGENCE_V0_1.md | Methodology, metrics, and boundaries |
| packages/domain-intelligence/ | Runnable core engine and minimal Bundle |
| skills/domain-intelligence-bootstrap/ | Skill routing new domains into the core workflow |
| DESIGN.md | Demo information architecture, visual system, and acceptance contract |
| docs/PROJECT_SCOPE_AND_ATTRIBUTION.md | Ownership, third-party sources, and redistribution boundaries |

## Release boundary and third-party sources

The old AI News Reader / AI News Radar compatibility interface had incomplete source coverage and has been removed from the project release surface. Its page, page-specific static assets/, and site.webmanifest are no longer entry points or maintained product surfaces; the root page now leads only to the Private Intelligence Observatory demo.

The retained scripts/update_news.py, data/, feeds/, .github/workflows/update-news.yml, skills/ai-news-radar/, and skills/radar/ are historical or experimental collection references, not the core methodology, product home, or an original “Bole Skill” of this project. They come from or are based on [LearnPrompt/ai-news-radar](https://github.com/LearnPrompt/ai-news-radar), under the MIT License. See [NOTICE](NOTICE.md) and [scope and attribution](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md) for directory-level attribution and redistribution rules.

Mature collection components may be reused at the boundary, but they do not replace domain-specific requirement modeling, historical evaluation, portfolio design, or coverage auditing.

## Local preview and validation

Start the demo:

~~~bash
python3 -m http.server 8080
~~~

Open http://127.0.0.1:8080/demo/.

Core tests and checks:

~~~bash
uv run --project packages/domain-intelligence pytest -q packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff format --check packages/domain-intelligence/src packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff check packages/domain-intelligence/src packages/domain-intelligence/tests
~~~

The project uses the MIT License. The core domain-intelligence methodology and additions are maintained by mizzlelover; retained upstream collection components preserve the [LearnPrompt/ai-news-radar](https://github.com/LearnPrompt/ai-news-radar) attribution and Copyright (c) 2026 LearnPrompt notice. See LICENSE, NOTICE.md, and the [scope and attribution document](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md).
