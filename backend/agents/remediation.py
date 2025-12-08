from typing import Dict, Any
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import parse_toon, to_toon
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain.agents import create_agent

class Remediation(BaseModel):
    explanation: str
    formatted_code: str

class RemediationAgent(BaseAgent):

    def __init__(self, config: AgentConfig = None):
        super().__init__(config)

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

        self.agent = self._create_agent()

    def _create_agent(self):
        """Create the ReAct agent with tools."""
        prompt = """
You are the Remediation Agent in a secure code repair pipeline.

You receive:
- Enriched vulnerability metadata (category, summary, code context)
- Possibly a code snippet to patch

Your responsibilities:

1. **Explain the vulnerability**
   - Provide a short, clear explanation of the root cause.
   - Use terminology appropriate to the category (SQL injection, RCE, secrets, XSS, etc.)
   - Do NOT restate metadata verbatim. Add insight.

2. **Provide the fixed code**
   - Rewrite ONLY the vulnerable portion.
   - Produce safe, correct, minimal, production-ready code.
   - Do not introduce unrelated changes.

3. **Output Format**
   Return ONLY this JSON (no markdown, no code fences):

   {
     "explanation": "<short human-readable description of the vulnerability>",
     "formatted_code": "the diff of the CODE"
   }

Rules:
- The output must be valid JSON and must match the Pydantic model exactly.
- Never output anything outside the JSON object.
"""
        
        # Create the agent
        agent = create_agent(
            model=self.llm,
            system_prompt=prompt,
            response_format=Remediation
        )
    
        return agent

    async def _generate_patch(self, enriched: Dict[str, Any]):
        """
        Generate a security patch using LLM.
        """

        # Pull fields from enriched vulnerability output
        category = enriched.get("category", "Unknown")
        summary = enriched.get("summary", "No summary provided.")

        attack_vector = enriched.get("attack_vector", "UNKNOWN")
        attack_complexity = enriched.get("attack_complexity", "LOW")
        privileges_required = enriched.get("privileges_required", "NONE")
        user_interaction = enriched.get("user_interaction", "NONE")

        impact_confidentiality = enriched.get("impact_confidentiality", "LOW")
        impact_integrity = enriched.get("impact_integrity", "LOW")
        impact_availability = enriched.get("impact_availability", "LOW")
        code = enriched.get("code_snippet")

        prompt = f"""
You are a secure code repair system. Your job is to generate safe, correct, minimal patches.

==================== VULNERABILITY CONTEXT ====================
Category: {category}
Summary: {summary}

Exploitability:
- attack_vector: {attack_vector}
- attack_complexity: {attack_complexity}
- privileges_required: {privileges_required}
- user_interaction: {user_interaction}

Impact:
- Confidentiality: {impact_confidentiality}
- Integrity: {impact_integrity}
- Availability: {impact_availability}

======================== BUGGY CODE ===========================
{code}

============================ TASK =============================
Produce ONLY a unified diff patch with an explanation that fixes the vulnerability.

====================== REQUIRED FORMAT =========================
```patch
diff --git a/FILE.py b/FILE.py
--- a/FILE.py
+++ b/FILE.py
@@
<your fixed code diff here>
RULES:

Output ONLY the patch.

No explanations, no commentary.

The diff must be valid and minimal.

Do not modify unrelated parts of the file.
    """

        try:
            result = await self.agent.ainvoke({
            "messages": [{"role": "user", "content": prompt}]
        })

            remedy = result["structured_response"]
            return remedy.model_dump()
        
        except Exception as e:
            return {
                "patch": f"ERROR: {e}",
                "explanation": "Model generation failed."
            }



    async def _execute(self, state: ScanState) -> Dict[str, Any]:
        """
        Generate patches for enriched vulnerabilities and secrets.
        """


        enriched_vulns = state.get("enriched_vulnerabilities", [])
        enriched_secrets = state.get("enriched_secrets", [])
        code_scanner_vulns = state.get("vulnerabilities", [])

        self.logger.info(
            f"Generating remediation for {len(enriched_vulns)} vulnerabilities "
            f"and {len(enriched_secrets)} secrets"
        )

        vuln_patches = []

        # Generate patches for vulnerabilities
        for i, vuln_toon in enumerate(enriched_vulns):
            enriched_data = parse_toon(vuln_toon)
            self.logger.debug(f"Vuln {i} enriched_data file field: {enriched_data.get('file')}")
            
            # Get original vulnerability data (with file/line info)
            original_vuln = parse_toon(code_scanner_vulns[i]) if i < len(code_scanner_vulns) else {}
            self.logger.debug(f"Vuln {i} original_vuln file field: {original_vuln.get('file')}")

            patches = await self._generate_patch(enriched_data)

            # Merge enriched data, patches, and original file/line metadata
            combined = {
                **enriched_data,
                **patches,
                "file": original_vuln.get("file", enriched_data.get("file", "unknown")),
                "ln": original_vuln.get("ln", enriched_data.get("ln", "")),
            }
            self.logger.debug(f"Vuln {i} combined file field: {combined.get('file')}")
            vuln_patches.append(to_toon(combined))

        secret_patches = []
        code_scanner_secrets = state.get("secrets", [])
        
        for i, sec_toon in enumerate(enriched_secrets):
            sec = parse_toon(sec_toon)
            self.logger.debug(f"Secret {i} enriched file field: {sec.get('file')}")
            
            # Get original secret data (with file/line info)
            original_secret = parse_toon(code_scanner_secrets[i]) if i < len(code_scanner_secrets) else {}
            self.logger.debug(f"Secret {i} original file field: {original_secret.get('file')}")

            record = {
                **sec,
                "fix_type": "remove_secret",
                "recommendation": "Move the secret to environment variables or a secure storage system.",
                # Ensure file and ln are preserved from original if not in enriched
                "file": sec.get("file", original_secret.get("file", "unknown")),
                "ln": sec.get("ln", original_secret.get("ln", "")),
            }
            self.logger.debug(f"Secret {i} final file field: {record.get('file')}")

            secret_patches.append(to_toon(record))

        return {
            "vulnerability_patches": vuln_patches,
            "secret_patches": secret_patches,
            "status": "remediation_complete"
        }