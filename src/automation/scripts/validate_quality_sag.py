from validator_utils import ensure_exists, load_json

SCHEMA_FILES = [
    "agents/contracts/quality_sag_request.schema.json",
    "agents/contracts/quality_sag_response.schema.json",
]

EXAMPLES = [
    "agents/contracts/examples/quality-sag/request.json",
    "agents/contracts/examples/quality-sag/response.json",
]


def main() -> None:
    for path in SCHEMA_FILES + EXAMPLES:
        ensure_exists(path)
        load_json(path)
    print("QualitySAG contracts and examples parsed successfully.")


if __name__ == "__main__":
    main()
