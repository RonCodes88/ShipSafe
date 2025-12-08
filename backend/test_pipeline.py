
import os
import asyncio
import httpx
import sys
from dotenv import load_dotenv
load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  
PROJECT_ROOT = os.path.dirname(ROOT_DIR)
sys.path.append(PROJECT_ROOT)


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_URL = "https://github.com/cywlol/repo-to-test-shipsafe"

# Import your LangGraph workflow
from graph.workflow import create_scan_workflow
from graph.state import ScanState


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

    print("\n================= FINAL STATE =================")
    print(result_state)

    print("\n================= REPO METADATA ===============")
    print(result_state.get("repo_metadata"))

    print("\n================= FILE COUNT ==================")
    files = result_state.get("files", {})
    print(f"Fetched {len(files)} files")

    print("\n================= FIRST 5 FILE PATHS ==========")
    for path in list(files.keys())[:5]:
        print(path)

    # Close HTTP client
    await http_client.aclose()


# Run async test
if __name__ == "__main__":
    asyncio.run(main())
