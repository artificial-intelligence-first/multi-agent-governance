# Contracts

JSON Schemas and related examples defining payloads exchanged between agents.

* `knowledge_request.schema.json` / `knowledge_response.schema.json` - payload
  definitions for KnowledgeMag knowledge curation tasks.
* `docs_sag_request.schema.json` / `docs_sag_response.schema.json` - payload
  definitions for DocsSAG documentation drafting tasks.
* `prompt_sag_request.schema.json` / `prompt_sag_response.schema.json` - payload
  definitions for PromptSAG prompt engineering tasks.
* `context_sag_request.schema.json` / `context_sag_response.schema.json` - payload
  definitions for ContextSAG context engineering tasks.
* `result_envelope.schema.json` - canonical envelope used for agent outputs.

Example payloads live under `agents/contracts/examples/`. Use them in tests and CI to
catch regressions early.
