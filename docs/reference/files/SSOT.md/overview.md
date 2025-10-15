# Single Source of Truth (SSOT)

## Definition
A single source of truth (SSOT) is a governance principle that designates one authoritative location for a given dataset, document, or policy. All downstream systems must reference this source to avoid conflicting or redundant copies.

## Key Characteristics
- **Authoritative** — The SSOT is the canonical record; any discrepancies elsewhere must be reconciled back to it.
- **Accessible** — Stakeholders can read the SSOT easily, ensuring shared understanding of the current state.
- **Versioned** — Changes are tracked so teams can audit when and why updates occurred.

## Benefits
- Reduces data inconsistency and rework.
- Improves trust in automation by eliminating ambiguity about “the latest truth”.
- Simplifies compliance reviews because auditors only need to verify the SSOT.

## Implementation Guidance
- Declare the SSOT explicitly (e.g., `agents/SSOT.md` at the repository root).
- Route all policy or terminology updates through the SSOT before propagating to other docs.
- Align automation (Flow Runner, agents) to read from the SSOT, not secondary copies.

## Update Log
- 2025-10-13 — Initial summary derived from public definitions of SSOT (e.g., Wikipedia) and tailored to the Multi Agent Governance repository.

## Source
- https://en.wikipedia.org/wiki/Single_source_of_truth
