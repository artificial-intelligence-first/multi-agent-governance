.PHONY: validate test validate-knowledge validate-docs-sag validate-prompt validate-context \
        validate-workflow validate-operations validate-qa validate-quality validate-reference \
        validate-sop validate-skills setup-flow-runner pilot-skills-phase1 pilot-skills-phase2

PYTHON ?= $(shell if [ -x .venv/bin/python ]; then printf '.venv/bin/python'; else command -v python3; fi)

validate: validate-knowledge validate-docs-sag validate-prompt validate-context \
          validate-workflow validate-operations validate-qa validate-quality validate-reference \
          validate-sop validate-skills

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

validate-sop:
	$(PYTHON) src/automation/scripts/validate_sop.py

validate-skills:
	$(PYTHON) src/automation/scripts/validate_skills.py

setup-flow-runner:
	bash src/automation/scripts/setup_flow_runner.sh

pilot-skills-phase1:
	PYTHONPATH=src/mcprouter/src $(PYTHON) src/automation/scripts/analyze_skills_pilot.py \
		--dataset skills/pilot/phase1/dataset.jsonl --top-k 3 --threshold 0.75

pilot-skills-phase2:
	PYTHONPATH=src/mcprouter/src $(PYTHON) src/automation/scripts/analyze_skills_pilot.py \
		--dataset skills/pilot/phase2/dataset.jsonl --top-k 3 --threshold 0.75 --skills-exec

test:
	$(PYTHON) -m pytest
