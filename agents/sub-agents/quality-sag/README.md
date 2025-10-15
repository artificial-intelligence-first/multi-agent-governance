# QualitySAG

QualitySAG supplements QAMAG by checking PLANS.md consistency and surfacing
potential quality risks early in the workflow.

## Inputs
- `PLANS.md`
- `.runs/<run_id>/` artefacts generated to date

## Outputs
- `.runs/<run_id>/quality/quality_notes.json`
- Inline comments or warnings passed back to WorkFlowMAG
