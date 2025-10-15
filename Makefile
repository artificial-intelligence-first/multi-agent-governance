.PHONY: validate test validate-knowledge validate-docs-sag validate-prompt validate-context \
        validate-workflow validate-operations validate-qa validate-quality validate-reference \
        setup-flow-runner

PYTHON ?= $(shell if [ -x .venv/bin/python ]; then printf '.venv/bin/python'; else command -v python3; fi)

validate: validate-knowledge validate-docs-sag validate-prompt validate-context \
          validate-workflow validate-operations validate-qa validate-quality validate-reference

validate-knowledge:
	$(PYTHON) src/automation/scripts/validate_knowledge.py

validate-docs-sag:
	$(PYTHON) src/automation/scripts/validate_docs_sag.py

validate-prompt:
	$(PYTHON) src/automation/scripts/validate_prompt_sag.py

validate-context:
	$(PYTHON) src/automation/scripts/validate_context_sag.py

validate-workflow:
	$(PYTHON) src/automation/scripts/validate_workflow.py

validate-operations:
	$(PYTHON) src/automation/scripts/validate_operations.py

validate-qa:
	$(PYTHON) src/automation/scripts/validate_qa.py

validate-quality:
	$(PYTHON) src/automation/scripts/validate_quality_sag.py

validate-reference:
	$(PYTHON) src/automation/scripts/validate_reference_sag.py

setup-flow-runner:
	bash src/automation/scripts/setup_flow_runner.sh

test:
	$(PYTHON) -m pytest
