# Shared Workflow Steps

This directory stores reusable workflow fragments. Reference them from agent
workflows using relative paths (e.g., `../../../shared/workflows/steps/preflight_check.wf.yaml`).

Convention:
- Filenames use snake_case with `.wf.yaml` suffix.
- Each file should include `version`, `name`, and `description` fields.
- Steps must be idempotent and avoid agent-specific assumptions.
- Document required inputs for each step. For example, `preflight_check.wf.yaml`
  expects `with.preflight_path` so adopters can point to their own SOP file.
