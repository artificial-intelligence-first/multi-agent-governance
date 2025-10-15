from validator_utils import ensure_exists, load_json

SCHEMA_FILES = [
    "agents/contracts/qa_request.schema.json",
    "agents/contracts/qa_response.schema.json",
]

EXAMPLES = [
    "agents/contracts/examples/qa/request.json",
    "agents/contracts/examples/qa/response.json",
]


def main() -> None:
    for path in SCHEMA_FILES + EXAMPLES:
        ensure_exists(path)
        load_json(path)
    print("QAMAG contracts and examples parsed successfully.")


if __name__ == "__main__":
    main()
