# Private Intelligence Observatory

## Domain Intelligence Methodology and Briefing System

**Give me a domain. Private Intelligence Observatory builds the domain's knowledge and intelligence system, then keeps it current.**

[![Private Intelligence Observatory CI](https://github.com/mizzlelover/private-intelligence-observatory/actions/workflows/domain-intelligence.yml/badge.svg)](https://github.com/mizzlelover/private-intelligence-observatory/actions/workflows/domain-intelligence.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[Try the demo](https://mizzlelover.github.io/private-intelligence-observatory/demo/) · [Visual reading room](https://mizzlelover.github.io/private-intelligence-observatory/demo/reading.html) · [Practitioner guide](docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md) · [Core methodology](docs/DOMAIN_INTELLIGENCE_V0_1.md) · [Source scale and activation](docs/SOURCE_PORTFOLIO_SCALE.md) · [Source activation run](docs/SOURCE_ACTIVATION_RUN.md) · [Engine](packages/domain-intelligence/README.md) · [Scope and attribution](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md) · [中文](README.md)

---

## This is not another AI news reader

Most AI assistants, daily briefings, and knowledge engines are built around AI practitioners tracking AI. Professionals in tourism, manufacturing, education, agriculture, healthcare, energy, city building, and other domains also need to track policy, projects, technology, competition, supply chains, and markets. Very few tools help them turn that need into a durable operating system.

The real gap is not simply whether a tool exists. The people who need this capability most often do not know what their domain contains, who is worth following, which source is trustworthy, or even which professional question to ask first. Existing AI tools usually begin with a prompt, a source configuration, or a daily digest, leaving the most important domain map for the user to discover alone.

**Private Intelligence Observatory reduces the entry to one action: give it a domain, and it builds the knowledge and intelligence system that domain needs.** Enter “digital tourism,” “robotics,” or any professional field. The system expands the boundary, vocabulary, observation surfaces, people, organizations, experts, source roles, evidence, and knowledge gaps before adding briefs, notifications, and a maintainable knowledge engine. It is especially useful when you are entering a domain and do not yet know who to follow or trust.

Experts, websites, reports, or project materials you already have can be added later by telling the AI to attach them to the domain. They enrich the foundation; they are not an entry requirement.

People who can already configure sources, build daily briefings, and maintain an AI knowledge engine on their own are not the primary audience. They may reuse the engineering pieces, but they are not the gap this project is designed to close.

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
→ Source Activation / Evidence Records
→ Knowledge-domain Delta
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

## A private observatory needs a source network with real scale

Private Intelligence Observatory is not a few dozen links wrapped in a daily digest. A real domain network needs multiple layers: standards and policy, research and experts, procurement and delivery evidence, platforms and vendors, open-source ecosystems, and early signals from newsletters, podcasts, media, and communities.

The [source scale and activation rules](docs/SOURCE_PORTFOLIO_SCALE.md) document this “expand, replay, then activate” model. A concrete domain's source network, historical evidence, and local acquisition snapshots belong to a run workspace, not to the public product code or repository examples.

## Start from a domain

You may only have the name of an industry, sector, or knowledge domain. You do not know where to start, which expert to trust, or which sources deserve a place in your working system. Open the [demo](https://mizzlelover.github.io/private-intelligence-observatory/demo/) and enter a domain keyword such as “digital tourism” to preview how a domain expands into a foundation, observation surfaces, participants, experts, and sources. This is a static interaction demo; it does not perform live research or generate a real briefing. To build a domain in practice, follow the [user guide](docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md) into the core Skill and engine.

Once you have built the foundation in the actual workflow, tell the AI to add any experts, websites, reports, or project materials you already use. Then add a focused question when you are ready; neither action replaces the domain-first entry.

### If you are an engineering collaborator

Start with the [engine](packages/domain-intelligence/README.md) and the [Bootstrap Skill](skills/domain-intelligence-bootstrap/SKILL.md). The engine handles EAR, point-in-time replay, source portfolios, source activation, evidence conversion, coverage audits, and domain-ranked briefs. Collection, databases, email, delivery, and web presentation remain replaceable boundary adapters. Their job is to keep the domain knowledge base reliable after the domain-first entry.

Minimal runnable example:

~~~bash
uv run --project packages/domain-intelligence dib \
  packages/domain-intelligence/examples/data-elements.json \
  --output-dir out/domain-intelligence
~~~

For the complete domain workflow, the Skill creates a local typed seed Bundle. The domain name is the only domain input a practitioner needs to provide; the Bundle and snapshots stay in the local run workspace:

~~~bash
uv run --project packages/domain-intelligence dib \
  --domain "your domain" \
  --bundle /path/to/local/domain-seed.json \
  --snapshots /path/to/local/snapshots \
  --output-dir /tmp/private-intelligence-run
~~~

The run writes the domain profile, source map, acquisition plan, source activation, knowledge graph, daily brief JSON/Markdown, Bootstrap report, and `run-manifest.json`. `--snapshots` is a reproducible local acquisition adapter; live RSS, API, browser, or authenticated adapters remain replaceable boundary components.

## Repository map

| Path | Purpose |
| --- | --- |
| demo/ | Audience-facing product demo, domain-first entry, and methodology visuals |
| docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md | Application guide for non-technical users |
| docs/DOMAIN_INTELLIGENCE_V0_1.md | Methodology, metrics, and boundaries |
| docs/SOURCE_PORTFOLIO_SCALE.md | Source-network scale, layers, and activation states |
| docs/SOURCE_ACTIVATION_RUN.md | Acquisition runs, evidence records, daily signals, and knowledge-domain deltas |
| packages/domain-intelligence/ | Runnable core engine and minimal Bundle |
| skills/domain-intelligence-bootstrap/ | Skill routing new domains into the core workflow |
| DESIGN.md | Demo information architecture, visual system, and acceptance contract |
| docs/PROJECT_SCOPE_AND_ATTRIBUTION.md | Ownership, third-party sources, and redistribution boundaries |

## Release boundary and third-party sources

The current public surface is the Private Intelligence Observatory demo and reading room. The AI News Reader / AI News Radar compatibility page and its page-specific static assets/ and site.webmanifest are not product entry points.

The retained scripts/update_news.py, data/, feeds/, .github/workflows/update-news.yml, skills/ai-news-radar/, and skills/radar/ are collection or consumption references, not the core methodology or an original “Bole Skill” of this project. They come from or are based on [LearnPrompt/ai-news-radar](https://github.com/LearnPrompt/ai-news-radar), under the MIT License. See [NOTICE](NOTICE.md) and [scope and attribution](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md) for directory-level attribution and redistribution rules.

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
