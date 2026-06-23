"""Load procurement mock datasets from project-local JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOCK_DATA_DIR = _PROJECT_ROOT / "mock_data"


def _load_dataset(filename: str) -> list[dict[str, Any]]:
    """Read a mock data JSON file and return its parsed list payload."""
    file_path = _MOCK_DATA_DIR / filename
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def load_budgets() -> list[dict[str, Any]]:
    """Load and return budget records from mock_data/budgets.json."""
    return _load_dataset("budgets.json")


def load_vendors() -> list[dict[str, Any]]:
    """Load and return vendor records from mock_data/vendors.json."""
    return _load_dataset("vendors.json")


def load_policies() -> list[dict[str, Any]]:
    """Load and return policy records from mock_data/policies.json."""
    return _load_dataset("policies.json")


def load_requests() -> list[dict[str, Any]]:
    """Load and return purchase request records from mock_data/requests.json."""
    return _load_dataset("requests.json")
