"""
Simple CLI helper to hit the /ingest endpoint for a local folder.
Usage: python scripts/ingest_local.py ./data/raw
"""

import sys

import requests


def main() -> None:
    folder = sys.argv[1] if len(sys.argv) > 1 else "./data/raw"
    response = requests.post("http://localhost:8000/ingest", json={"path": folder, "source_type": "local"})
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
