"""Deterministic OpenAPI specification export script."""

import json
import sys
from pathlib import Path

from vistaro.main import app


def export_openapi(target_path: Path) -> None:
    """Export the FastAPI application OpenAPI schema to a deterministic JSON file."""
    schema = app.openapi()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    # Deterministic sort and formatting with trailing newline
    content = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    target_path.write_text(content, encoding="utf-8")
    sys.stdout.write(f"Exported OpenAPI specification to {target_path}\n")


def main() -> None:
    """CLI entry point."""
    script_dir = Path(__file__).resolve().parent
    api_dir = script_dir.parent
    output_file = api_dir / "openapi.json"
    export_openapi(output_file)


if __name__ == "__main__":
    main()
