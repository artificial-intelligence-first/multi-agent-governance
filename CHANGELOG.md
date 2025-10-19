# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- BrowserSAG sub-agent with Chrome DevTools, Playwright, and MarkItDown MCP integrations plus validation workflow.
- GovernanceSAG sub-agent and Flow Runner governance stage for automated AGENTS/SSOT/CHANGELOG/PLANS audits.
- MarkItDown / Playwright MCP reference documentation and validation scripts.
- Prompt stage Codex integration can optionally run review prompts and capture dedicated artifacts.

### Changed
- Updated AGENTS, SSOT, MCP configuration, and WorkFlowMAG docs to reflect the new browser/governance workflows.
- Flow Runner orchestration now includes browser and governance stages with refreshed configs and task scaffolds.
- Expanded `.gitignore` to keep validation telemetry runs out of version control.

### Fixed
- Ensured Flow Runner pytest configuration reliably imports local task modules during repository runs.
- Governance SSOT audit now checks `.mcp/SSOT.md` rather than `.mcp/AGENTS.md`.
