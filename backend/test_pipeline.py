import asyncio
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  
PROJECT_ROOT = os.path.dirname(ROOT_DIR)               
sys.path.append(PROJECT_ROOT)

from agents.code_scanner import CodeScannerAgent
from agents.context_enricher import ContextEnricherAgent
from graph.state import ScanState
from agents.secret_detector import SecretDetectorAgent


async def test_pipeline():
    state = ScanState({
        "repo_metadata": {
            "name": "demo",
            "files": [
                {
                    "path": "app.py",
                    "content": """
import os
import json
import random
import requests


encoded_key = "QUtJQUlPU0ZPRE5ON0VYQU1QTEU="  # decodes to AKIAIOSFODNN7EXAMPLE
password = "supersecretpassword123"
SESSION_TOKEN = "b29a9dd3e80f49dfb27e019c97b43e24"
example_string = "thisismaybeapasswordbutnotreally"
fake_token = "token12345"
encoded_message = "SGVsbG8sIHRoaXMgaXMganVzdCBhIHRlc3Qu"


def load_config(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


class UserService:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_user(self, user_id):
        resp = requests.get(f"{self.db_url}/user/{user_id}")
        if resp.status_code == 200:
            return resp.json()
        return None


def compute_value(x, y):
    if y == 0:
        return None
    return (x * 42) / y + random.random()


class DataCache:
    def __init__(self):
        self.cache = {}

    def store(self, key, value):
        # High-entropy random key (may or may not be detected)
        cache_key = "k9F9d3Lm8vN2pQ4rT8Wx"
        self.cache[cache_key] = value

    def fetch(self, key):
        return self.cache.get(key, None)


API_SECRET_HASH = "4f9b1c7fa2e84fdc9b348a9d4c2ef781"


def greet(name):
    print(f"Hello, {name}!")


def unsafe():
    os.system(input("cmd: "))
"""
                }
            ]
        },
        "vulnerabilities": [],
        "secrets": [],
        "enriched_vulnerabilities": [],
        "enriched_secrets": [],
        "vulnerability_patches": [],
        "secret_patches": [],
        "agent_trace": []
    })

    print("\n=== Running Code Scanner ===")
    scanner = CodeScannerAgent()
    scanner_output = await scanner._execute(state)
    state.update(scanner_output)

    print("\n=== Running Secret Detector Agent ===")
    secret_detector = SecretDetectorAgent()
    secret_output = await secret_detector._execute(state)
    state.update(secret_output)

    print("\n=== Running Context Enricher ===")
    enricher = ContextEnricherAgent()
    enricher_output = await enricher._execute(state)
    state.update(enricher_output)

    print("\n=== Running Remediation Agent ===")
    remediation = RemediationAgent()
    remediation_output = await remediation._execute(state)
    state.update(remediation_output)

    print("\n=== FINAL STATE ===")
    print(state)

    print("\n=== GENERATED PATCHES ===")
    for p in state.get("vulnerability_patches", []):
        print("\n--- Vulnerability Patch ---")
        print(p)

    for p in state.get("secret_patches", []):
        print("\n--- Secret Patch ---")
        print(p)
