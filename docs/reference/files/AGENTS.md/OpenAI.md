# AGENTS.md Overview

## Summary
- AGENTS.md is a Markdown convention introduced by OpenAI and partner teams to give AI coding agents a predictable, machine-focused playbook that complements human-facing docs like README.md (sources: agents.md site, GitHub repository).
- The format has become a de facto standard across 20,000+ open-source repositories and is supported by major agent platforms such as Codex, Cursor, RooCode, Gemini, VS Code integrations, and more (sources: InfoQ coverage, agents.md announcements, partner press).

## Key Details
- **Placement & scope**: Repositories place an AGENTS.md at the root; large monorepos may add nested AGENTS.md files so agents read the closest instructions (sources: agents.md documentation, InfoQ interview).
- **Content expectations**: Common sections cover dev environment setup, build/test commands, linting, security, and PR policies—essentially the operational knowledge an AI needs to edit and validate code safely (sources: agents.md documentation, GitHub spec, partner playbooks).
- **Conflict resolution**: When multiple files exist, agents prioritise the most specific (nearest) AGENTS.md; explicit user prompts override file guidance (sources: agents.md FAQ, InfoQ interview).
- **Tool integration**: Vendors including OpenAI Codex, Google’s Jules, Cursor, VS Code, and others recognise the format, enabling consistent automation without per-tool config files (sources: adoption notes on agents.md, partner announcements, InfoQ coverage).
- **Community stewardship**: The spec is maintained in the open (MIT-licensed) via GitHub, with ongoing discussion about scope, terminology, and evolution to stay vendor-neutral (sources: GitHub repository README and issues, agents.md roadmap).
- **Minimal example**: A concise template outlining dev environment tips, testing steps, and PR expectations is available in `sample.md` within this directory for quick adoption in new repositories.

## Dependencies
- Ensure the Multi Agent System’s own `AGENTS.md` stays aligned with this upstream guidance so local automation inherits the standard structure.
- Cross-reference `agents/SSOT.md` when introducing glossary or contract updates to keep terminology consistent for both human and agent consumers.
- Use DocsSAG outputs (`docs/generated/`) to document implementation-specific instructions, linking back to AGENTS.md sections when relevant.

## Sample AGENTS.md file

### Dev environment tips
- Use `pnpm dlx turbo run where <project_name>` to jump to a package instead of scanning with `ls`.
- Run `pnpm install --filter <project_name>` to add the package to your workspace so Vite, ESLint, and TypeScript can see it.
- Use `pnpm create vite@latest <project_name> -- --template react-ts` to spin up a new React + Vite package with TypeScript checks ready.
- Check the name field inside each package's package.json to confirm the right name—skip the top-level one.

### Testing instructions
- Find the CI plan in the .github/workflows folder.
- Run `pnpm turbo run test --filter <project_name>` to run every check defined for that package.
- From the package root you can just call `pnpm test`. The commit should pass all tests before you merge.
- To focus on one step, add the Vitest pattern: `pnpm vitest run -t "<test name>"`.
- Fix any test or type errors until the whole suite is green.
- After moving files or changing imports, run `pnpm lint --filter <project_name>` to be sure ESLint and TypeScript rules still pass.
- Add or update tests for the code you change, even if nobody asked.

### PR instructions
- Title format: [<project_name>] <Title>
- Always run `pnpm lint` and `pnpm test` before committing.

## Update Log
- 2025-10-13: Populated overview with upstream specification details and adoption context (sources synced the same day).

## Source
https://agents.md (last synced: 2025-10-13)
https://github.com/openai/agents.md (last synced: 2025-10-13)