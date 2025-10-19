---
name: api-design
description: >
  Apply to REST and OpenAPI design tasks: draft CRUD resources, pagination contracts, request/response schemas, HTTP status guidance, rate limit headers, and governance-aligned API documentation.
---

# API Design Skill

> Apply this Skill whenever you introduce or modify REST/HTTP APIs. It aligns interface decisions with governance policies and prepares assets for downstream automation.

## Quick start
- Gather context: product goals, consumer personas, required integrations, latency/availability SLAs.
- Confirm non-goals and auth model (service-to-service, user-facing, token scopes).
- Outline resources and operations using CRUD+custom verbs; prefer nouns for resource paths (`/projects/{id}`).
- Define request/response payloads using JSON Schema snippets; ensure consistent casing (snake_case for field names).
- Capture error model (HTTP status, machine-readable `code`, human-readable `message`) and retry expectations.
- Update `skills/api-design/resources/openapi-template.md` with new paths/examples; share with DocsSAG for publication.
- Run contract validation (e.g., `make validate-knowledge`) once schemas/payloads are committed.

## Design checklist
- Structural consistency
  - [ ] Resource names are plural nouns (`/projects`, `/projects/{project_id}/members`).
  - [ ] Query parameters documented with defaults and type constraints.
  - [ ] Pagination uses `page_token` + `page_size` or cursor-based pattern.
- Authentication & authorization
  - [ ] Auth mechanism documented (bearer token, HMAC, OAuth client creds).
  - [ ] Scopes/permissions mapped to operations.
  - [ ] Error codes for auth failures (`401`, `403`) include actionable remediation guidance.
- Versioning
  - [ ] Default path version (`/v1/`) or header strategy declared.
  - [ ] Breaking change policy referenced (see `agents/SSOT.md` glossary for “API versioning”).
- Observability & limits
  - [ ] Rate limits documented; include headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`).
  - [ ] idempotency guidance for unsafe methods (POST/DELETE) provided.
  - [ ] Logging/trace correlation fields identified (`request_id`, `traceparent`).

## Examples
- Drafting a new `projects` API → clone resource outline from previous `skills/api-design/resources/openapi-template.md`, replace sample schema, update tags.
- Reviewing a change request → compare proposed payload diff with checklist; flag missing error handling or incomplete pagination.
- Preparing public docs → convert template section into user-facing copy and share with DocsSAG for formatting.

## Resources
- [`resources/openapi-template.md`](resources/openapi-template.md) — starter OpenAPI snippet with info section, paths, components.
- `docs/reference/tool/openapi/` (if present) — authoritative style guidance; ensure cross-reference when available.
- `docs/reference/files/SKILL.md/Anthropic.md` — reference for structuring Skills and progressive disclosure.

## Script usage
- No executable scripts yet. If automation is required (e.g., schema lint), place scripts under `scripts/` and register them in `skills/ALLOWLIST.txt` before enabling execution.
