Source: https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/introduction-prompt-design (last synced: 2025-10-13)
Source: https://deepmind.google/research/publications/83400/ (last synced: 2025-10-13)
Source: https://deepmind.google/research/publications/90773/ (last synced: 2025-10-13)

# Google Prompt Design References

## Summary
- Aggregates Google Cloud Vertex AI prompt design guidance and Google DeepMind research on prompting strategies.
- Provides a consolidated view so the Multi Agent Governance can compare prompting techniques across vendors when building automation and documentation.

## Key Details
- **Vertex AI introduction**: Covers prompt structure fundamentals (instructions, context, output specs, examples) and discusses how to iterate for clarity and reliability.
- **Multimodal prompts**: Google Cloud documentation outlines how to combine text, images, and other modalities; note requirements when the Multi Agent Governance expands beyond text-only use cases.
- **Testing & evaluation**: Recommends evaluating prompts with varied inputs, capturing metrics, and using Vertex AI tools for prompt optimization.
- **DeepMind research (paper 83400)**: Investigates advanced prompting methods and explores performance trade-offs between prompt tuning, few-shot, and fine-tuning approaches.
- **DeepMind research (paper 90773)**: Focuses on reasoning and chain-of-thought prompting; highlights techniques for structured problem solving and self-consistency.
- **Comparative insight**: These resources highlight when prompt iteration is sufficient versus when model adaptation or additional context is needed.

## Dependencies
- Align Multi Agent Governance prompts with root AGENTS guardrails (testing, safe edits, logging) regardless of vendor guidance.
- Document prompt experiments in DocsSAG so human review stays in sync with automation practices.
- Consider API-specific limits (token windows, multimodal capabilities) when porting Google prompt techniques into this repository.

## Update Log
- 2025-10-13: Initial consolidation of Google Cloud Vertex AI and Google DeepMind prompt references.
