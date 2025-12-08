
import os
import asyncio
import httpx
import sys

import json
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  
PROJECT_ROOT = os.path.dirname(ROOT_DIR)
sys.path.append(PROJECT_ROOT)


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_URL = "https://github.com/cywlol/repo-to-test-shipsafe"

from graph.workflow import create_scan_workflow
from graph.state import ScanState

def print_section(title: str):
    print(f"\n{'=' * 20} {title} {'=' * 20}")

async def main():
    http_client = httpx.AsyncClient()
    app = create_scan_workflow(http_client)

    # Build initial state
    initial_state: ScanState = {
        "repo_url": REPO_URL,
        "github_token": GITHUB_TOKEN,
        "vulnerabilities": [],
        "enriched_vulnerabilities": [],
        "vulnerability_patches": [],
        "secrets": [],
        "enriched_secrets": [],
        "secret_patches": [],
        "repo_metadata": {},
        "errors": [],
        "status": "starting",
        "agent_trace": [],
        "execution_time": 0.0,
    }

    print("\n Running vulnerability scan workflow…\n")

    # Run workflow
    result_state = await app.ainvoke(initial_state)


    print_section("FINAL STATE (Pretty Printed)")
    print(json.dumps(result_state, indent=4))   # JSON-style readable formatting

    print_section("FILES SUMMARY")
    files = result_state.get("files", {})
    print(f"Fetched {len(files)} files")

    print_section("FIRST 5 FILE PATHS")
    for path in list(files.keys())[:5]:
        print(f" - {path}")


    # Close HTTP client
    await http_client.aclose()


# Run async test
if __name__ == "__main__":
    asyncio.run(main())
