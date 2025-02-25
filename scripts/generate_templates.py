# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "ruamel-yaml",
# ]
# ///
"""Generates YAML templates based on the JSON schema.

It handles conditional properties, but only when the condition is based on the 'type' or 'collection' property.

Usage:
    Easiest way to run the script is to use `uv`, which handles the dependencies automatically:

        uv run generate_templates.py

    If run without arguments, it will generate templates for all resource types and save them to the `../yaml_templates`
    directory.
"""

import argparse
import json
import sys
from pathlib import Path

import ruamel.yaml

SCRIPT_PATH = Path(__file__).resolve().parent
DEFAULT_SCHEMA = SCRIPT_PATH / "../schema/metadata.json"
DEFAULT_OUTPUT = SCRIPT_PATH / "../yaml_templates"
TYPES = ["corpus", "lexicon", "model", "analysis", "utility", "collection"]


def generate_yaml_template(schema: dict, schema_type: str) -> ruamel.yaml.CommentedMap:
    """Parse schema and return a dictionary with template data.

    Args:
        schema: JSON schema as a dictionary.
        schema_type: Type of the resource to generate a template for.

    Returns:
        A dictionary with template data.
    """
    yaml_output = ruamel.yaml.CommentedMap()

    def parse_schema_properties(properties: dict, output: ruamel.yaml.CommentedMap) -> None:
        for key, value in properties.items():
            output[key] = value.get("default", "")
            if value.get("description"):
                output.yaml_add_eol_comment(value["description"], key=key)

            # Recursively handle nested objects
            if value["type"] == "object":
                output[key] = ruamel.yaml.CommentedMap()
                parse_schema_properties(value.get("properties", {}), output[key])
            elif value["type"] == "array":
                output[key] = []
                item_schema = value.get("items", {})
                if "properties" in item_schema:
                    array_item = ruamel.yaml.CommentedMap()
                    parse_schema_properties(item_schema["properties"], array_item)
                    output[key].append(array_item)
                else:
                    pass

    # Add conditional properties
    for conditional in schema.get("allOf", []):
        type_cond = conditional["if"]["properties"].get("type")
        if (type_cond and (type_cond.get("const") == schema_type or schema_type in type_cond.get("enum", []))) or (
            conditional["if"]["properties"].get("collection", {}).get("const") and schema_type == "collection"
        ):
            schema.get("properties", {}).update(conditional["then"]["properties"])

    parse_schema_properties(schema.get("properties", {}), yaml_output)

    # Set a few hardcoded values
    if schema_type == "collection":
        yaml_output["collection"] = True
        yaml_output["type"] = ""
        yaml_output.yaml_add_eol_comment("Must be one of: " + ", ".join(TYPES), key="type")
    else:
        yaml_output["type"] = schema_type

    return yaml_output


def main() -> None:
    """Handle command line arguments and call template generation."""
    parser = argparse.ArgumentParser(description="Generate YAML template based on JSON schema")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="Path to the JSON schema file")
    parser.add_argument("--type", default="all", choices=[*TYPES, "all"], help="Resource type to generate template for")
    parser.add_argument(
        "output_path",
        nargs="?",
        default=DEFAULT_OUTPUT,
        help="Path (file or dir) for saving the generated YAML template(s)",
    )

    args = parser.parse_args()

    schema_file = Path(args.schema)
    if not schema_file.is_file():
        print("Schema file does not exist.")
        sys.exit(1)

    output_path = Path(args.output_path)
    if args.type == "all" and not output_path.is_dir():
        print("Output path must be a directory when using type 'all'.")
        sys.exit(1)

    # Load JSON schema
    with schema_file.open(encoding="UTF-8") as schema_file:
        schema = json.load(schema_file)

    types = TYPES if args.type == "all" else [args.type]

    for schema_type in types:
        # Generate YAML template based on schema type
        yaml_output = generate_yaml_template(schema, schema_type)
        output_file = output_path / f"{schema_type}.yaml" if output_path.is_dir() else output_path

        # Save the generated YAML template to a file
        yaml = ruamel.yaml.YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        with output_file.open("w", encoding="UTF-8") as f:
            yaml.dump(yaml_output, f)

        print(f"YAML template for resource type '{args.type}' has been saved to '{output_file.resolve()}'.")


if __name__ == "__main__":
    main()
