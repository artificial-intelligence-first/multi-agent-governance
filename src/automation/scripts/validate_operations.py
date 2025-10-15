from validator_utils import ensure_exists, load_json

SCHEMA_FILES = [
    "agents/contracts/operations_request.schema.json",
    "agents/contracts/operations_response.schema.json",
]

EXAMPLES = [
    "agents/contracts/examples/operations/request.json",
    "agents/contracts/examples/operations/response.json",
]


def main() -> None:
    for path in SCHEMA_FILES + EXAMPLES:
        ensure_exists(path)
        load_json(path)
    print("OperationsMAG contracts and examples parsed successfully.")


if __name__ == "__main__":
    main()
