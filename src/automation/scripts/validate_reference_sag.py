from validator_utils import ensure_exists, load_json

SCHEMA_FILES = [
    "agents/contracts/reference_sag_request.schema.json",
    "agents/contracts/reference_sag_response.schema.json",
]

EXAMPLES = [
    "agents/contracts/examples/reference-sag/request.json",
    "agents/contracts/examples/reference-sag/response.json",
]


def main() -> None:
    for path in SCHEMA_FILES + EXAMPLES:
        ensure_exists(path)
        load_json(path)
    print("ReferenceSAG contracts and examples parsed successfully.")


if __name__ == "__main__":
    main()
