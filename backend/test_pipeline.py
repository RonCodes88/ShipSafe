import asyncio
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  
PROJECT_ROOT = os.path.dirname(ROOT_DIR)               
sys.path.append(PROJECT_ROOT)

from agents.code_scanner import CodeScannerAgent
from agents.context_enricher import ContextEnricherAgent
from graph.state import ScanState


async def test_pipeline():
    state = ScanState({
        "repo_metadata": {
            "name": "demo",
            "files": [
                {
                    "path": "app.py",
                    "content": """
import os

def unsafe():
    os.system(input("cmd: "))
"""
                }
            ]
        },
        "vulnerabilities": [],
        "secrets": [],
        "agent_trace": []
    })

    scanner = CodeScannerAgent()
    scanner_output = await scanner._execute(state)
    state.update(scanner_output)

    enricher = ContextEnricherAgent()

    enricher_output = await enricher._execute(state)
    state.update(enricher_output)
    print(state)


asyncio.run(test_pipeline())
