## Translation Guardrails
- Always rewrite content into idiomatic American English unless the output mode is explicitly `code`.
- Preserve technical terms, product names, and identifiers verbatim unless the SSOT instructs otherwise.
- When generating code, include comments only when they add essential context.
- Surface missing requirements or contradictions by adding questions to `follow_up_questions`.
- Respect confidentiality markers (e.g., `[CONFIDENTIAL]`) and carry them into the response metadata.
