"""Context Enrichment Agent - Semantic understanding and context enhancement with ReAct."""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import parse_toon, to_toon
from langchain.agents import create_agent
# from langchain.tools import tool
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI


# class CVEMatch(BaseModel):
#     cve_id: str
#     description: str
#     cvss: Optional[float]



class EnrichedOutput(BaseModel):
    category: str
    summary: str

    attack_vector: str
    attack_complexity: str
    privileges_required: str
    user_interaction: str

    impact_confidentiality: str
    impact_integrity: str
    impact_availability: str

    # cvss_score: float
    # cve_matches: List[CVEMatch]

class ContextEnricherAgent(BaseAgent):
    """
    Context Enrichment Agent enhances vulnerability findings with semantic understanding.
    
    Uses ReAct agent with tools to:
    - Cross-reference with CVE databases and security advisories
    - Add attack vector analysis
    - Add impact assessment
    - Use RAG for contextual understanding
    """
    
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
You are the ShipSafe Context Enrichment Agent.

Your mission is to transform raw vulnerability findings into enriched,
semantically accurate security assessments.

You receive:
- A code snippet (if available)
- Metadata including file path, severity, detector signals, and ML probability

Your job:

============================================================
1. CLASSIFY THE VULNERABILITY
============================================================
Determine the most accurate security category such as:
- SQL Injection
- Command Injection
- Remote Code Execution (RCE)
- Path Traversal
- Hardcoded Secrets
- Insecure Randomness
- Weak Cryptography
- XSS
- SSRF
- Deserialization
- Authorization Bypass
- Others (use best judgment)

Output a concise root-cause summary explaining *what the bug is* and
*why it is dangerous*.

============================================================
2. EXPLOITABILITY ANALYSIS (CVSS-style reasoning)
============================================================
Infer these fields using only the code and metadata:

- attack_vector: ["NETWORK", "ADJACENT", "LOCAL", "PHYSICAL"]
- attack_complexity: ["LOW", "HIGH"]
- privileges_required: ["NONE", "LOW", "HIGH"]
- user_interaction: ["NONE", "REQUIRED"]

Use reasoning based on:
- How input reaches the vulnerable code
- Whether exploitation requires user action or privileges
- Whether the vulnerability is reachable remotely, locally, etc.

============================================================
3. IMPACT ANALYSIS (CIA TRIAD)
============================================================
Determine realistic impact values:

- impact_confidentiality: ["NONE", "LOW", "HIGH"]
- impact_integrity: ["NONE", "LOW", "HIGH"]
- impact_availability: ["NONE", "LOW", "HIGH"]

Base this on what the vulnerable code can expose or damage.

============================================================
4. OUTPUT REQUIREMENTS
============================================================
You must output ONLY a JSON object matching EXACTLY the schema:

{
  "category": string,
  "summary": string,

  "attack_vector": string,
  "attack_complexity": string,
  "privileges_required": string,
  "user_interaction": string,

  "impact_confidentiality": string,
  "impact_integrity": string,
  "impact_availability": string
}

No markdown.  
No explanation outside the JSON.  
No additional fields beyond the schema.

Stay concise, technically accurate, and deterministic.
"""

        
        # Create the agent
        agent = create_agent(
            model=self.llm,
            system_prompt=prompt,
            response_format=EnrichedOutput
        )
    
        return agent
    
    async def _enrich_vulnerability(self, vuln_data: Dict[str, Any], state: ScanState) -> Dict[str, Any]:
        """
        Enrich a vulnerability using structured LLM output (EnrichedOutput).
        """
        self.logger.debug(f"Input vuln_data: {vuln_data}")
        vuln_type = vuln_data.get("vuln", "UNKNOWN")
        severity = vuln_data.get("sev", "MEDIUM")
        file_path = vuln_data.get("file", "unknown")
        line_range = vuln_data.get("ln", "unknown")
        ml_prob = vuln_data.get("prob", "N/A")
        code_type = vuln_data.get("type", "unknown")


        code_snippet = self._get_code_snippet(state, file_path, line_range)

        prompt = f"""
You are the **ShipSafe Context Enrichment Agent**, an advanced security
analysis system that enriches raw vulnerability findings with deeper
context, semantics, and exploit reasoning.
Analyze the following vulnerability and return ONLY structured JSON matching the EnrichedOutput schema.

VULNERABILITY DETAILS:
- Type: {vuln_type}
- Severity: {severity}
- File: {file_path}
- Line Range: {line_range}
- ML Probability: {ml_prob}
- Code Type: {code_type}

CODE SNIPPET:
{code_snippet}

Return only JSON. No explanations.
    """
        try:
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })

            enriched_model = result["structured_response"]
            # Preserve original metadata (file, ln) and add enriched data
            merged_result = {
                **enriched_model.model_dump(),  # Add enriched fields first
                **vuln_data,  # Then add original fields (will override any conflicts)
                "code_snippet": code_snippet
            }
            # Explicitly ensure file and ln are preserved
            if "file" in vuln_data:
                merged_result["file"] = vuln_data["file"]
            if "ln" in vuln_data:
                merged_result["ln"] = vuln_data["ln"]
            
            self.logger.debug(f"Merged result file field: {merged_result.get('file')}, ln: {merged_result.get('ln')}")
            return merged_result

        except Exception as e:
            self.logger.error(f"Error enriching vulnerability: {e}", exc_info=True)
            # Safe fallback structure - preserve original fields
            return {
                **vuln_data,  # Preserve original fields
                "category": "Unknown",
                "summary": "Analysis failed.",
                "attack_vector": "LOCAL",
                "attack_complexity": "LOW",
                "privileges_required": "NONE",
                "user_interaction": "NONE",
                "impact_confidentiality": "LOW",
                "impact_integrity": "LOW",
                "impact_availability": "LOW",
            }
    
    async def _enrich_secret(self, secret_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a secret using the same EnrichedOutput structured schema.
        """
        self.logger.debug(f"Input secret_data: {secret_data}")
        secret_type = secret_data.get("secret", "UNKNOWN")
        severity = secret_data.get("sev", "HIGH")

        prompt = f"""
You are the **ShipSafe Context Enrichment Agent**, an advanced security
analysis system that enriches raw vulnerability findings with deeper
context, semantics, and exploit reasoning.
Analyze the following hardcoded secret and return ONLY structured JSON
matching the EnrichedOutput schema.

SECRET DETAILS:
- Type: {secret_type}
- Severity: {severity}

Treat this as a security vulnerability.
Populate cve_matches as an empty list if irrelevant.
Return only JSON.
"""

        try:
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })


            enriched_model = result["structured_response"]
            # Preserve original metadata (file, ln, type) and add enriched data
            merged_result = {
                **enriched_model.model_dump(),  # Add enriched fields first
                **secret_data  # Then add original fields (will override any conflicts)
            }
            # Explicitly ensure file and ln are preserved
            if "file" in secret_data:
                merged_result["file"] = secret_data["file"]
            if "ln" in secret_data:
                merged_result["ln"] = secret_data["ln"]
            if "type" in secret_data:
                merged_result["type"] = secret_data["type"]
            
            self.logger.debug(f"Merged secret result file field: {merged_result.get('file')}, ln: {merged_result.get('ln')}")
            return merged_result

        except Exception as e:
            self.logger.error(f"Error enriching secret: {e}", exc_info=True)
            return {
                **secret_data,
                "category": "Hardcoded Secret",
                "summary": "Analysis failed.",
                "attack_vector": "LOCAL",
                "attack_complexity": "LOW",
                "privileges_required": "NONE",
                "user_interaction": "NONE",
                "impact_confidentiality": "LOW",
                "impact_integrity": "LOW",
                "impact_availability": "LOW",
                # "cvss_score": 0.0,
                # "cve_matches": [],
            }
    # def estimate_cvss(attack_vector: str, impact_conf: str, impact_integ: str, impact_avail: str) -> float:
    #     """
    #     Estimate CVSS score when official CVSS is missing.
    #     Returns a number between 0.0 and 10.0.

    #     Inputs:
    #     - attack_vector: NETWORK, ADJACENT, LOCAL, PHYSICAL
    #     - impact_conf: NONE, LOW, HIGH
    #     - impact_integ: NONE, LOW, HIGH
    #     - impact_avail: NONE, LOW, HIGH
    #     """

    #     # Base scores for attack vectors
    #     av_score = {
    #         "NETWORK": 0.85,
    #         "ADJACENT": 0.62,
    #         "LOCAL": 0.55,
    #         "PHYSICAL": 0.20
    #     }.get(attack_vector.upper(), 0.55)

    #     imp_map = {"NONE": 0.0, "LOW": 0.22, "HIGH": 0.56}

    #     conf = imp_map.get(impact_conf.upper(), 0)
    #     integ = imp_map.get(impact_integ.upper(), 0)
    #     avail = imp_map.get(impact_avail.upper(), 0)

    #     impact_subscore = 1 - ((1 - conf) * (1 - integ) * (1 - avail))

    #     cvss = round(min(10.0, av_score * 3.5 + impact_subscore * 6.5), 1)
    #     return cvss

    # def search_cve(keyword: str, limit: int = 5):
    #     """
    #     Search NVD CVE database using keyword.
    #     Returns top matches with CVE ID + description + CVSS if present.
    #     """
    #     NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    #     params = {
    #         "keywordSearch": keyword,
    #         "resultsPerPage": limit,
    #     }

    #     try:
    #         r = requests.get(NVD_API, params=params, timeout=5)
    #         data = r.json()

    #         results = []

    #         for item in data.get("vulnerabilities", []):
    #             cve = item["cve"]
    #             cve_id = cve["id"]

    #             description = cve["descriptions"][0]["value"]

    #             cvss = None
    #             if "metrics" in cve:
    #                 cvss_data = cve["metrics"].get("cvssMetricV31") or cve["metrics"].get("cvssMetricV30")
    #                 if cvss_data:
    #                     cvss = cvss_data[0]["cvssData"]["baseScore"]

    #             cwe = None

    #             if "weaknesses" in cve:
    #                 try:
    #                     cwe = cve["weaknesses"][0]["description"][0]["value"]
    #                 except Exception:
    #                     pass

    #             if not cwe:
    #                 try:
    #                     cwe = cve["problemtype"]["problemtype_data"][0]["description"][0]["value"]
    #                 except Exception:
    #                     pass


    #             results.append({
    #                 "cve_id": cve_id,
    #                 "description": description,
    #                 "cwe": cwe,
    #                 "cvss": cvss
    #             })

    #         return results

    #     except Exception as e:
    #         return [{"error": str(e)}]

        

    
    def _get_code_snippet(self, state: ScanState, file_path: str, line_range: str) -> str:
        """
        Extract the actual code snippet from repo metadata.
        
        Args:
            state: Current scan state
            file_path: Path to the file
            line_range: Line range in format "start-end"
            
        Returns:
            Code snippet string
        """
        try:
            # Get files from repo metadata
            content = state.get("files")[file_path]
            if "-" in line_range:
                start, end = map(int, line_range.split("-"))
                lines = content.split("\n")
                
                # Extract the specific lines (with some context)
                context_before = max(0, start - 3)
                context_after = min(len(lines), end + 3)
                
                snippet_lines = lines[context_before:context_after]
                snippet = "\n".join(snippet_lines)
                
                return f"Lines {context_before+1}-{context_after}:\n{snippet}"
            
            # If no line range, return first 20 lines
            lines = content.split("\n")[:20]
            return "\n".join(lines)
                        
        except Exception as e:
            self.logger.error(f"Error extracting code snippet: {e}")
            return "Code snippet extraction failed"
    
    async def _execute(self, state: ScanState) -> Dict[str, Any]:
        """
        Enrich vulnerability and secret findings with context using ReAct agent.
        
        Args:
            state: Current scan state
            
        Returns:
            Dictionary with enriched vulnerabilities and secrets in TOON format
        """
        vulnerabilities = state.get("vulnerabilities", [])
        secrets = state.get("secrets", [])
        
        self.logger.info(
            f"Enriching {len(vulnerabilities)} vulnerabilities "
            f"and {len(secrets)} secrets with agent"
        )
        
        # Enrich vulnerabilities using ReAct agent
        enriched_vulnerabilities = []
        for vuln_toon in vulnerabilities:
            vuln_data = parse_toon(vuln_toon)
            enriched_data = await self._enrich_vulnerability(vuln_data, state)
            enriched_vulnerabilities.append(to_toon(enriched_data))
        
        # Enrich secrets using ReAct agent
        enriched_secrets = []
        for secret_toon in secrets:
            secret_data = parse_toon(secret_toon)
            enriched_data = await self._enrich_secret(secret_data)
            enriched_secrets.append(to_toon(enriched_data))
        
        self.logger.info(f"Context enrichment complete: Secrets: {enriched_secrets} \n Vuln : {enriched_vulnerabilities}")
        
        return {
            "enriched_vulnerabilities": enriched_vulnerabilities,
            "enriched_secrets": enriched_secrets,
            "status": "enrichment_complete",
        }
    