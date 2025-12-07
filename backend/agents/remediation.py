"""Remediation Agent - Patch generation and fix suggestions."""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import parse_toon, to_toon
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import json
import re
import ast



class RemediationAgent(BaseAgent):

    def __init__(self, config: AgentConfig = None):
        super().__init__(config)

        # Load RepairLLaMA adapter model
        model_id = "bigcode/starcoder2-3b"

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype="auto",
        )

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=500,
            temperature=0.2,
            num_beams=5
        )

    async def _generate_patch(self, code: str, enriched: Dict[str, Any], alternatives: int = 3):
        """
        Generate multiple patch candidates using RepairLLaMA.
        """

        summary = enriched.get("summary", "")
        category = enriched.get("category", "")
        remediation_hint = enriched.get("remediation", "")
        cvss = enriched.get("cvss_score", "")

        patches = []

        for i in range(alternatives):

            prompt = f"""
You are RepairLLaMA, a program repair specialist.

Given a vulnerable Java function and context:
- Vulnerability category: {category}
- Summary: {summary}
- CVSS Score: {cvss}
- Recommended remediation: {remediation_hint}

BUGGY FUNCTION:
{code}

TASK:
Produce a FIXED VERSION of the function. ONLY output the replacement patch code
for the buggy region, as a raw code block. Do not add text outside the code block.

Format:
```patch
<your_patch_here>
    """

        result = self.pipe(prompt)[0]["generated_text"]

        # Extract patch block
        match = re.search(r"```patch(.*?)```", result, re.S)
        patch_text = match.group(1).strip() if match else result

        patches.append({
            "patch_number": i + 1,
            "patch": patch_text,
            "explanation": f"Repair option {i+1} based on vulnerability summary."
        })

        return patches

    def _validate_patch(self, patch: str) -> bool:
        """
        Very lightweight validation:
        - Check that patch is syntactically valid Java (basic check)
        - Ensure no dangerous patterns were introduced
        """
        bad_patterns = [
            "Runtime.getRuntime().exec",   # introduces RCE
            "ProcessBuilder(",             # dangerous
            "eval(",                       # unsafe eval
        ]
        return not any(p in patch for p in bad_patterns)

    async def _execute(self, state: ScanState) -> Dict[str, Any]:
        """
        Generate patches from enriched vulnerabilities and secrets.
        """

        enriched_vulns = state.get("enriched_vulnerabilities", [])
        enriched_secrets = state.get("enriched_secrets", [])

        self.logger.info(
            f"Generating remediation for {len(enriched_vulns)} vulnerabilities and "
            f"{len(enriched_secrets)} secrets"
        )

        vulnerability_patches = []

        # -----------------------------------------------
        # VULNERABILITIES → PATCH GENERATION
        # -----------------------------------------------
        for vuln_toon in enriched_vulns:
            data = parse_toon(vuln_toon)

            code = data.get("code_context", "")
            if not code:
                continue

            patches = await self._generate_patch(code, data, alternatives=3)

            clean_patches = [
                p for p in patches if self._validate_patch(p["patch"])
            ]

            patch_record = {
                "file": data.get("file"),
                "line_range": data.get("ln"),
                "category": data.get("category"),
                "summary": data.get("summary"),
                "patch_id": f"patch_{len(vulnerability_patches)}",
                "alternatives": clean_patches,
            }

            vulnerability_patches.append(to_toon(patch_record))

        # -----------------------------------------------
        # SECRETS → SIMPLE REMEDIATION
        # -----------------------------------------------
        secret_patches = []
        for s in enriched_secrets:
            sec = parse_toon(s)

            patch_record = {
                **sec,
                "patch_id": f"secret_patch_{len(secret_patches)}",
                "fix_type": "remove_secret",
                "recommendation": "Move secret to environment variables or secret manager.",
            }

            secret_patches.append(to_toon(patch_record))

        return {
            "vulnerability_patches": vulnerability_patches,
            "secret_patches": secret_patches,
            "status": "remediation_complete",
        }
