import asyncio
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  
PROJECT_ROOT = os.path.dirname(ROOT_DIR)
sys.path.append(PROJECT_ROOT)

from agents.remediation import RemediationAgent
from utils.toon_parser import to_toon
from graph.state import ScanState


async def test_remediation_only():

    # Create FAKE enriched vulnerabilities in real TOON format
    enriched_vuln = to_toon({
        "category": "Command Injection",
        "summary": "Untrusted input flows directly into os.system(), enabling arbitrary command execution.",
        "attack_vector": "NETWORK",
        "attack_complexity": "LOW",
        "privileges_required": "NONE",
        "user_interaction": "NONE",

        "impact_confidentiality": "HIGH",
        "impact_integrity": "HIGH",
        "impact_availability": "HIGH",

        "cvss_score": 9.8,

        "cve_matches": [
            {
                "cve_id": "CVE-2023-12345",
                "description": "Command injection vulnerability",
                "cvss": 9.8
            }
        ],

        "remediation": "Never pass untrusted input to execution functions. Sanitize or whitelist commands.",
        "file": "service.py",
        "ln": "1-3",

        # Required for patch generation:
        "code_context": """def unsafe():
    os.system(input("cmd: "))
"""
    })

    # Fake enriched secret also in TOON format:
    enriched_secret = to_toon({
        "secret": "supersecretpassword123",
        "type": "Hardcoded Password",
        "sev": "HIGH",
        "remediation": "Move secrets into environment variables or a secret manager.",
        "file": "config.py",
        "ln": "10"
    })

    # Build a minimal state that simulates after ContextEnricherAgent
    state = ScanState({
        "repo_metadata": {
            "name": "fake_repo",
            "files": [
                {
                    "path": "service.py",
                    "content": """
def unsafe():
    os.system(input("cmd: "))
"""
                }
            ]
        },

        "enriched_vulnerabilities": [enriched_vuln],
        "enriched_secrets": [enriched_secret],

        "vulnerability_patches": [],
        "secret_patches": [],
        "agent_trace": []
    })

    print("\n=== Running RemediationAgent (TOON-only test) ===")
    remediation = RemediationAgent()
    output = await remediation._execute(state)

    print("\n=== REMEDIATION OUTPUT ===")
    print(output)

    print("\n=== GENERATED VULNERABILITY PATCHES ===")
    for p in output.get("vulnerability_patches", []):
        print("\n--- Patch TOON ---")
        print(p)

    print("\n=== GENERATED SECRET PATCHES ===")
    for p in output.get("secret_patches", []):
        print("\n--- Secret Patch TOON ---")
        print(p)


asyncio.run(test_remediation_only())
