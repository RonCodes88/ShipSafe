from typing import Dict, Any
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import parse_toon, to_toon
from langchain_ollama import ChatOllama
import re


class RemediationAgent(BaseAgent):

    def __init__(self, config: AgentConfig = None):
        super().__init__(config)

        self.llm = ChatOllama(
            model="llama3",
            temperature=0
        )

    async def _generate_patch(self, code: str, enriched: Dict[str, Any], alternatives: int = 3):
        """
        Generate multiple patch candidates using an LLM.
        """

        summary = enriched.get("summary", "")
        category = enriched.get("category", "")
        remediation_hint = enriched.get("remediation", "")
        cvss = enriched.get("cvss_score", "")

        patches = []

        for i in range(alternatives):

            prompt = f"""
You are a secure code repair system. Your task is to generate correct and safe patches.

VULNERABILITY CONTEXT:
- Category: {category}
- Summary: {summary}
- CVSS Score: {cvss}
- Recommended remediation: {remediation_hint}

BUGGY CODE:
{code}

sql
Copy code

TASK:
Return ONLY the FIXED code in a patch format like:

```patch
<patch_here>
RULES:

No explanations outside the code block.

Only output the corrected patch.

Do NOT repeat the prompt.
"""

            try:
                res = await self.llm.ainvoke(prompt)
                text = res.content
            except Exception as e:
                patches.append({
                    "patch_number": i + 1,
                    "patch": f"ERROR: {e}",
                    "explanation": "Model generation failed."
                })
                continue

        # Extract ```patch ... ```
            match = re.search(r"```patch(.*?)```", text, re.S)
            patch_text = match.group(1).strip() if match else text.strip()

            patches.append({
                "patch_number": i + 1,
                "patch": patch_text,
                "explanation": f"Automated remediation option {i+1}."
            })

        return patches
    def _validate_patch(self, patch: str) -> bool:
        """
        Basic validation to ensure no dangerous patterns are introduced.
        """
        forbidden = [
            "Runtime.getRuntime().exec",
            "ProcessBuilder(",
            "eval("
            ]
        return not any(x in patch for x in forbidden)

    async def _execute(self, state: ScanState) -> Dict[str, Any]:
        """
        Generate patches for enriched vulnerabilities and secrets.
        """


        enriched_vulns = state.get("enriched_vulnerabilities", [])
        enriched_secrets = state.get("enriched_secrets", [])

        self.logger.info(
            f"Generating remediation for {len(enriched_vulns)} vulnerabilities "
            f"and {len(enriched_secrets)} secrets"
        )

        vuln_patches = []

        # Generate patches for vulnerabilities
        for vuln_toon in enriched_vulns:
            data = parse_toon(vuln_toon)
            code = data.get("code_context", "")

            if not code:
                continue

            patches = await self._generate_patch(code, data, alternatives=3)
            valid_patches = [p for p in patches if self._validate_patch(p["patch"])]

            record = {
                "file": data.get("file"),
                "line_range": data.get("ln"),
                "category": data.get("category"),
                "summary": data.get("summary"),
                "patch_id": f"patch_{len(vuln_patches)}",
                "alternatives": valid_patches
            }

            vuln_patches.append(to_toon(record))

        # Handle secret remediation
        secret_patches = []
        for sec_toon in enriched_secrets:
            sec = parse_toon(sec_toon)

            record = {
                **sec,
                "patch_id": f"secret_patch_{len(secret_patches)}",
                "fix_type": "remove_secret",
                "recommendation": "Move the secret to environment variables or a secure storage system."
            }

            secret_patches.append(to_toon(record))

        return {
            "vulnerability_patches": vuln_patches,
            "secret_patches": secret_patches,
            "status": "remediation_complete"
        }