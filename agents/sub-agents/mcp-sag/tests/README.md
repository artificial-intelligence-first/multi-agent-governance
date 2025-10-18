# MCPSAG Test Notes

- Unit and integration coverage for MCP routing lives in `src/mcprouter/tests` and `src/flowrunner/tests`. Run the targeted commands listed in `AGENTS.md` and `sop/README.md`.
- Add agent-specific tests here when MCPSAG gains bespoke automation (e.g., checklist parsers, validation scripts).
- Coordinate with OpsMAG before introducing fixtures that hit live MCP providers; prefer stubs or recorded responses.
