from validator_utils import ensure_exists, load_json

SCHEMA_FILES = [
    "agents/contracts/workflow_request.schema.json",
    "agents/contracts/workflow_response.schema.json",
]

EXAMPLES = [
    "agents/contracts/examples/workflow/request.json",
    "agents/contracts/examples/workflow/response.json",
]


def main() -> None:
    for path in SCHEMA_FILES + EXAMPLES:
        ensure_exists(path)
        load_json(path)
    print("WorkflowMAG contracts and examples parsed successfully.")


if __name__ == "__main__":
    main()
