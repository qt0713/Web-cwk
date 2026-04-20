# GenAI Conversation Excerpts (Supplementary Evidence)

This document records representative GenAI-assisted decisions and verification steps. It is aligned to the technical report declaration and demonstrates methodical, declared use rather than ad-hoc prompting.

Reporting window for submission packaging:
- 2026-04-10 to 2026-04-20
- In this exported transcript, available project-relevant interactions in this window are concentrated on 2026-04-19 to 2026-04-20.

## 1) Usage methodology applied
For each substantial task, the workflow followed four stages:
1. Define objective and constraints.
2. Use GenAI to generate options and implementation candidates.
3. Accept/reject suggestions with explicit rationale.
4. Validate outcomes through tests, endpoint checks, and runtime logs.

This structure was used for architecture, data import reliability, deployment decisions, and presentation refinement.

## 2) Excerpted evidence by phase

### Excerpt A - Scope definition and feature strategy
- Date window (inside reporting range): 2026-04-19
- Prompt context: choose project direction and map to assessment criteria.
- Representative user request excerpt: "help me complete this project, choose book metadata and recommendation API".
- GenAI-assisted output:
  - transformed rubric text into implementation milestones,
  - prioritized secure CRUD + recommendation + analytics,
  - produced deliverable-first plan (repo/docs/report/slides/tests).
- Decision outcome:
  - accepted: book metadata + recommendation API as main theme,
  - accepted: add analytics and dataset integration to exceed minimum pass requirements.

### Excerpt B - Authentication design alternatives
- Date window (inside reporting range): 2026-04-19 to 2026-04-20
- Option exploration prompted with trade-off focus:
  - API key only,
  - JWT-based login flow,
  - Swagger-compatible OAuth2 password flow.
- Decision outcome:
  - accepted: JWT login/token flow for protected routes and oral defensibility,
  - rejected: API-key-only model as final approach because it provided weaker evidence of modern auth practice.
- Verification evidence:
  - successful token issuance,
  - protected endpoints returning expected auth behavior.

### Excerpt C - Data import robustness improvements
- Date window (inside reporting range): 2026-04-19 to 2026-04-20
- Problem context: Kaggle dataset import failed under multiple real-world file irregularities.
- GenAI-assisted debugging scope:
  - encoding issues,
  - malformed CSV rows,
  - NUL bytes,
  - ZIP-encapsulated CSV edge case,
  - ratings merge and column mismatch handling.
- Decision outcome:
  - accepted: resilient import script with fallback parsing and merge logic,
  - accepted: evidence-oriented command workflow with count verification.
- Verification evidence:
  - import result: Inserted = 1000, Skipped = 0,
  - database count and analytics endpoints returned consistent post-import data.

### Excerpt D - Deployment option analysis and fallback engineering
- Date window (inside reporting range): 2026-04-20
- Deployment options explored with constraints:
  - PythonAnywhere free-tier constraints,
  - Render constraints,
  - Tencent Cloud CVM + Nginx + systemd,
  - temporary reverse tunnel for stable oral demonstration.
- Decision outcome:
  - accepted: CVM deployment as primary runtime setup,
  - accepted: reverse tunnel as contingency when external inbound route was unstable,
  - rejected: relying on a single platform path without fallback.
- Verification evidence:
  - service active via systemd,
  - local and reverse-proxy health/docs checks returned 200,
  - public tunnel successfully exposed /health and /docs.

### Excerpt E - Submission artifact refinement
- Date window (inside reporting range): 2026-04-20
- GenAI-assisted tasks:
  - align technical report to implemented state,
  - add deployment evidence section,
  - convert slide outline into practical presentation template variants.
- Decision outcome:
  - accepted: concise, evidence-first report structure,
  - accepted: slide versions for 10-slide and <=6-slide oral delivery constraints.

## 3) What was not delegated to GenAI
- Final architecture selection and scope control.
- Runtime troubleshooting decisions under deployment constraints.
- Acceptance/rejection of suggested code edits.
- Final submission content and evidence packaging.

## 4) Validation and control record
- Automated validation: pytest integration checks.
- Runtime validation: local health/docs, protected endpoint behavior, analytics outputs.
- Deployment validation: service status, reverse proxy behavior, public demo path checks.
- Documentation validation: final consistency review across README, report, and slides.

## 5) Traceability
- Full conversation history is retained in local editor storage.
- This file intentionally includes concise excerpts and decision outcomes for examiner review.
- Raw JSONL-format snippet evidence is provided in `docs/GENAI_EXPORTED_LOG_SNIPPETS.md` for auditability.

## 6) Verbatim snippet examples (timestamped)
- 2026-04-19T19:19:04Z (user): "help me complete this project, choose book metadata and recommendation API".
- 2026-04-19 to 2026-04-20 (session phase): repeated troubleshooting on auth flow, dataset import robustness, and deployment access behavior.
- 2026-04-20 (submission phase): requests to align report content, slide template content, and GenAI declaration evidence with implemented project state.

These snippets are included as representative anchors. Detailed full-turn records remain available in the retained local transcript.
