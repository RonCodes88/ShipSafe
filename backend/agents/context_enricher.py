"""Context Enrichment Agent - Semantic understanding and context enhancement with ReAct."""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import parse_toon, to_toon
import requests
import json
from langchain.agents import create_agent
from langchain.tools import tool
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI


class CVEMatch(BaseModel):
    cve_id: str
    description: str
    cvss: Optional[float]

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

    cvss_score: float
    cve_matches: List[CVEMatch]

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
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Create the ReAct agent
        self.agent = self._create_agent()
    
    def _create_tools(self):
        """Create tools for the ReAct agent."""
        

        NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

        @tool
        def search_cve(keyword: str, limit: int = 5):
            """
            Search NVD CVE database using keyword.
            Returns top matches with CVE ID + description + CVSS if present.
            """

            params = {
                "keywordSearch": keyword,
                "resultsPerPage": limit,
            }

            try:
                r = requests.get(NVD_API, params=params, timeout=5)
                data = r.json()

                results = []

                for item in data.get("vulnerabilities", []):
                    cve = item["cve"]
                    cve_id = cve["id"]

                    description = cve["descriptions"][0]["value"]

                    cvss = None
                    if "metrics" in cve:
                        cvss_data = cve["metrics"].get("cvssMetricV31") or cve["metrics"].get("cvssMetricV30")
                        if cvss_data:
                            cvss = cvss_data[0]["cvssData"]["baseScore"]

                    cwe = None

                    if "weaknesses" in cve:
                        try:
                            cwe = cve["weaknesses"][0]["description"][0]["value"]
                        except Exception:
                            pass

                    if not cwe:
                        try:
                            cwe = cve["problemtype"]["problemtype_data"][0]["description"][0]["value"]
                        except Exception:
                            pass


                    results.append({
                        "cve_id": cve_id,
                        "description": description,
                        "cwe": cwe,
                        "cvss": cvss
                    })

                return results

            except Exception as e:
                return [{"error": str(e)}]

        @tool
        def estimate_cvss(attack_vector: str, impact_conf: str, impact_integ: str, impact_avail: str) -> float:
            """
            Estimate CVSS score when official CVSS is missing.
            Returns a number between 0.0 and 10.0.

            Inputs:
            - attack_vector: NETWORK, ADJACENT, LOCAL, PHYSICAL
            - impact_conf: NONE, LOW, HIGH
            - impact_integ: NONE, LOW, HIGH
            - impact_avail: NONE, LOW, HIGH
            """

            # Base scores for attack vectors
            av_score = {
                "NETWORK": 0.85,
                "ADJACENT": 0.62,
                "LOCAL": 0.55,
                "PHYSICAL": 0.20
            }.get(attack_vector.upper(), 0.55)

            imp_map = {"NONE": 0.0, "LOW": 0.22, "HIGH": 0.56}

            conf = imp_map.get(impact_conf.upper(), 0)
            integ = imp_map.get(impact_integ.upper(), 0)
            avail = imp_map.get(impact_avail.upper(), 0)

            impact_subscore = 1 - ((1 - conf) * (1 - integ) * (1 - avail))

            cvss = round(min(10.0, av_score * 3.5 + impact_subscore * 6.5), 1)
            return cvss

        return [estimate_cvss, search_cve]
    
    def _create_agent(self):
        """Create the ReAct agent with tools."""
        prompt = """You are the **ShipSafe Context Enrichment Agent**, an advanced security
analysis system that enriches raw vulnerability findings with deeper
context, semantics, and exploit reasoning.

You receive:
- A code snippet or vulnerability description
- Metadata (file path, ML probability, type)
- Optional CVE search results from the `search_cve` tool

Your responsibilities:

1. **Understand the vulnerability**
   - Identify the most likely vulnerability category (e.g., SQL injection,
     command injection, deserialization, weak crypto, insecure randomness,
     hardcoded secrets, XSS, path traversal, SSRF, RCE, etc.)
   - Summarize the root cause clearly.

2. **Use tools when helpful**
   - Call `search_cve` with useful keywords related to the vulnerability.
   - Interpret the returned CVE data:
     - Use description text
     - Use CWE if present
     - Use CVSS if present
     - Use these to improve your classification and reasoning
   - Call `estimate_cvss` if `search_cve` does not return a CVSS if needed. 
    
3. **Attack Vector Analysis (CVSS Exploitability)**
   Infer the following fields:
   - attack_vector: One of ["NETWORK", "ADJACENT", "LOCAL", "PHYSICAL"]
   - attack_complexity: ["LOW", "HIGH"]
   - privileges_required: ["NONE", "LOW", "HIGH"]
   - user_interaction: ["NONE", "REQUIRED"]

   Base these on:
   - How the code receives input
   - Whether untrusted input reaches dangerous functions
   - Code context such as web handlers, APIs, CLI tools, file I/O, etc.
   - Any signals from CVE descriptions

4. **Impact Assessment (CIA Triad)**
   Infer the likely impact if exploited:
   - Confidentiality impact: ["NONE", "LOW", "HIGH"]
   - Integrity impact: ["NONE", "LOW", "HIGH"]
   - Availability impact: ["NONE", "LOW", "HIGH"]

5. **Severity & CVSS Estimation**
   - If CVSS score is provided from CVEs, use it.
   - If not, estimate CVSS based on your exploitability + impact reasoning.
   Provide a numeric CVSS score between 0.0 and 10.0.

6. **Remediation Guidance**
   - Provide one short, actionable recommendation to fix the issue.

7. **Output Structured JSON Only**
   Return the final result as a JSON dictionary with exactly these fields:

   {
     "category": string,
     "summary": string,

     "attack_vector": string,
     "attack_complexity": string,
     "privileges_required": string,
     "user_interaction": string,

     "impact_confidentiality": string,
     "impact_integrity": string,
     "impact_availability": string,

     "cvss_score": number,
     "cve_matches": [ { "cve_id": string, "description": string, "cvss": number | null } ],

     "remediation": string
   }

Rules:
- Always try to use the `search_cve` tool when beneficial.
- Base your reasoning on BOTH the code and CVE database findings.
- Do NOT hallucinate CVE IDs or CWE numbers.
- If no relevant CVEs exist, return an empty list for cve_matches.
- Keep outputs concise, accurate, and consistent.
"""
        
        # Create the agent
        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=prompt,
            response_format=EnrichedOutput
        )
    
        return agent
    
    async def _enrich_vulnerability(self, vuln_data: Dict[str, Any], state: ScanState) -> Dict[str, Any]:
        """
        Enrich a vulnerability using structured LLM output (EnrichedOutput).
        """
        vuln_type = vuln_data.get("vuln", "UNKNOWN")
        severity = vuln_data.get("sev", "MEDIUM")
        file_path = vuln_data.get("file", "unknown")
        line_range = vuln_data.get("ln", "unknown")
        ml_prob = vuln_data.get("prob", "N/A")
        code_type = vuln_data.get("type", "unknown")

        code_snippet = self._get_code_snippet(state, file_path, line_range)

        prompt = f"""
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

Use tools when helpful:
- search_cve(): find similar vulnerabilities and pull CVE metadata
- estimate_cvss(): estimate CVSS score if CVE does not provide one

Return only JSON. No explanations.
    """
        try:
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })

            enriched_model = result["structured_response"]
            return enriched_model.model_dump()

        except Exception as e:
            self.logger.error(f"Error enriching vulnerability: {e}", exc_info=True)
            # Safe fallback structure
            return {
                "category": "Unknown",
                "summary": "Analysis failed.",
                "attack_vector": "LOCAL",
                "attack_complexity": "LOW",
                "privileges_required": "NONE",
                "user_interaction": "NONE",
                "impact_confidentiality": "LOW",
                "impact_integrity": "LOW",
                "impact_availability": "LOW",
                "cvss_score": 0.0,
                "cve_matches": [],
                "code_context": code_snippet,
            }
    
    async def _enrich_secret(self, secret_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a secret using the same EnrichedOutput structured schema.
        """
        secret_type = secret_data.get("secret", "UNKNOWN")
        severity = secret_data.get("sev", "HIGH")

        prompt = f"""
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
            return enriched_model.model_dump()
            return enriched_data

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
                "cvss_score": 0.0,
                "cve_matches": [],
            }

    
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
            files = state.get("repo_metadata", {}).get("files", [])
            
            # Find the matching file
            for file_data in files:
                if file_data.get("path") == file_path:
                    content = file_data.get("content", "")
                    
                    # Parse line range
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
            
            return "Code snippet not available"
            
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
            f"and {len(secrets)} secrets with ReAct agent"
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
        
        self.logger.info("Context enrichment complete")
        
        return {
            "enriched_vulnerabilities": enriched_vulnerabilities,
            "enriched_secrets": enriched_secrets,
            "status": "enrichment_complete",
        }