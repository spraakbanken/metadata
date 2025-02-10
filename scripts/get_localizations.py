"""This script fetches metadata from the API or from metadata files and generates localization YAML files.

It extracts unique values for specific keys from the metadata and updates the corresponding
localization files if there are any changes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import requests
import yaml

LOCALIZATIONS_PATH = Path("../localizations")
TASK_FILE = LOCALIZATIONS_PATH / "task.yaml"
ANALYSIS_UNITS_FILE = LOCALIZATIONS_PATH / "analysis_unit.yaml"
KEYWORDS_FILE = LOCALIZATIONS_PATH / "keywords.yaml"


def get_localizations(source_type: str) -> None:
    """Fetch metadata and generate localization YAML files.

    Args:
        source_type (str): The type of source, either 'url' or 'file'.
    """
    if source_type == "url":
        metadata = fetch_json_data_from_url("https://ws.spraakbanken.gu.se/ws/metadata/")
    elif source_type == "file":
        metadata = fetch_json_data_from_files(Path("../yaml"))
    else:
        raise ValueError("Invalid source type. Use 'url' or 'file'.")

    analysis_units = get_values_by_key(metadata, "analysis_unit")
    make_yaml(analysis_units, ANALYSIS_UNITS_FILE)

    analysis_tasks = get_values_by_key(metadata, "task")
    make_yaml(analysis_tasks, TASK_FILE)

    keywords = get_values_by_key(metadata, "keywords")
    make_yaml(keywords, KEYWORDS_FILE, translations=False)

    print(
        f"\nDone! Remember to add the translations in '{ANALYSIS_UNITS_FILE.name}' "
        f"and '{TASK_FILE.name}' if any updates were made."
    )


def make_yaml(values_list: list[str], filepath: Path, translations: bool = True) -> None:
    """Create or update a YAML file with localization data.

    Args:
        values_list (list): List of values to be localized.
        filepath (Path): Path to the YAML file.
        translations (bool): Whether to include translations or not.
    """
    new_localizations = dict.fromkeys(values_list, "") if translations else values_list

    # Load existing localizations
    with filepath.open() as fp:
        try:
            previous_localizations = yaml.safe_load(fp)
            if previous_localizations is None:
                previous_localizations = {} if translations else []
        except yaml.YAMLError as exc:
            raise exc

    # Update localizations and write new file if needed
    has_changed = False
    if translations:
        for key in new_localizations:
            if key not in previous_localizations:
                previous_localizations[key] = new_localizations[key]
                has_changed = True
    elif new_localizations != previous_localizations:
        previous_localizations = new_localizations
        has_changed = True

    if has_changed:
        with filepath.open("w") as fp:
            yaml.dump(previous_localizations, fp, allow_unicode=True, sort_keys=False)
        print(f"Updated '{filepath}'")

    else:
        print(f"No changes detected in '{filepath}'")


def fetch_json_data_from_url(url: str) -> dict[str, Any]:
    """Fetch JSON data from the specified URL.

    Args:
        url (str): The URL to fetch JSON data from.

    Returns:
        dict: The parsed JSON data, or an empty dictionary if an error occurs.
    """
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return {}


def fetch_json_data_from_files(directory: Path) -> dict[str, Any]:
    """Fetch JSON data from all YAML files in the specified directory.

    Args:
        directory (Path): The directory containing JSON files.

    Returns:
        dict: The combined JSON data from all files, or an empty dictionary if an error occurs.
    """
    combined_data = {}
    for file_path in directory.rglob("*.yaml"):
        resource_name = file_path.stem
        try:
            with file_path.open() as file:
                data = yaml.safe_load(file)
                if isinstance(data, dict):
                    combined_data[resource_name] = data
                else:
                    print(f"Skipping non-dict JSON content in file: {file_path}")
        except (OSError, yaml.YAMLError) as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
    return combined_data


def get_values_by_key(data: dict[str, Any], target_key: str) -> list[str]:
    """Extract all unique values for a given key from nested JSON data.

    Args:
        data (dict): The JSON data to search through.
        target_key (str): The key whose values should be extracted.

    Returns:
        list: A sorted list of unique values found for the specified key.
    """
    values: set = set()

    def extract_values(obj: dict[str, Any] | list[Any]) -> None:
        """Recursively extracts values associated with the target key from nested JSON structures."""
        if isinstance(obj, list):
            for item in obj:
                extract_values(item)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if key == target_key:
                    if isinstance(value, list):
                        values.update(value)
                    elif isinstance(value, str):
                        values.add(value)
                    else:
                        print(
                            f"Error collecting value from '{key}': '{value}' due to type {type(value)}. "
                            "Skipping!",
                            file=sys.stderr
                        )
                else:
                    extract_values(value)

    extract_values(data)
    return sorted(values)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch metadata and generate localization YAML files.")
    parser.add_argument(
        "source_type",
        type=str,
        choices=["url", "file"],
        help="The type of source, either 'url' or 'file'."
    )
    # Print help message if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    get_localizations(args.source_type)
