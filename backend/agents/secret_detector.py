"""
Fast Secret Detection Agent:
Runs regex + entropy locally,
then classifies candidates using OpenAI with structured Pydantic output.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import to_toon
import json
import re
import math
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent


# ============================================================
# Utility functions
# ============================================================

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {c: s.count(c) for c in set(s)}
    return -sum((count / len(s)) * math.log2(count / len(s)) for count in freq.values())


# ============================================================
# Pydantic Models
# ============================================================

class SecretClassification(BaseModel):
    secret_value: str
    secret_type: str
    file: str
    line: int
    severity: str

class SecretClassificationList(BaseModel):
    items: List[SecretClassification]

# ============================================================
# Secret Detector Agent
# ============================================================

class SecretDetectorAgent(BaseAgent):

    def __init__(self, config: AgentConfig = None):
        super().__init__(config)

        # Use OpenAI-based agent with structured output
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

        self.agent = self._create_agent()

    # --------------------------------------------------------
    # Create Classification Agent
    # --------------------------------------------------------
    def _create_agent(self):
        prompt = """
You are the ShipSafe Secret Classification Agent.

You receive potential secrets extracted from code via regex / entropy heuristics.
Your task is to classify each candidate.

For EACH item you must produce:
{
  "secret_value": string,
  "secret_type": string,   // e.g., AWS_ACCESS_KEY, GITHUB_TOKEN, HIGH_ENTROPY_STRING
  "file": string,
  "line": number,
  "severity": string       // one of: LOW, MEDIUM, HIGH
}

Rules:
- Output ONLY a JSON list of objects — no markdown, no commentary.
- Ensure the JSON exactly matches the SecretClassification schema.
"""

        return create_agent(
            model=self.llm,
            system_prompt=prompt,
            response_format=SecretClassificationList
        )

    # --------------------------------------------------------
    # Local Detection (Regex + Entropy)
    # --------------------------------------------------------
    def extract_candidates(self, content: str):
        lines = content.split("\n")
        candidates = []

        regex_patterns = {
            "AWS_ACCESS_KEY": r"AKIA[0-9A-Z]{16}",
            "GITHUB_TOKEN": r"gh[pousr]_[A-Za-z0-9]{36}",
            "SLACK_TOKEN": r"xox[baprs]-[A-Za-z0-9-]{10,48}",
            "GENERIC_KEY": r"[A-Za-z0-9/\+=]{20,}",  # suspicious long tokens
        }

        for i, line in enumerate(lines, start=1):

            # Regex patterns
            for name, pattern in regex_patterns.items():
                for match in re.findall(pattern, line):
                    candidates.append({
                        "value": match,
                        "line": i,
                        "origin": name,
                        "entropy": shannon_entropy(match),
                    })

            # Entropy-only tokens
            tokens = re.findall(r"[A-Za-z0-9/\+=]{20,}", line)
            for tok in tokens:
                ent = shannon_entropy(tok)
                if ent > 3.5:
                    candidates.append({
                        "value": tok,
                        "line": i,
                        "origin": "high_entropy",
                        "entropy": ent,
                    })

        return candidates

    # --------------------------------------------------------
    # LLM Classification Using Structured Output
    # --------------------------------------------------------
    async def classify_candidates(self, file_path: str, candidates: List[dict]):

        if not candidates:
            return []

        prompt = f"""
Classify the following extracted secret candidates.

FILE: {file_path}

CANDIDATES:
{candidates}

Return ONLY the JSON list.
"""

        try:
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })

            structured = result["structured_response"]
            return [item.model_dump() for item in structured.items]

        except Exception as e:
            self.logger.error(f"Secret classification LLM error: {e}", exc_info=True)
            return []

    # --------------------------------------------------------
    # Execute Agent
    # --------------------------------------------------------
    async def _execute(self, state: ScanState) -> Dict[str, Any]:

        all_findings = []

        for path, content in state["files"].items():
            candidates = self.extract_candidates(content)
            findings = await self.classify_candidates(path, candidates)

            for f in findings:
                toon = to_toon({
                    "secret": f["secret_value"][:30] + "...",
                    "type": f["secret_type"],
                    "sev": f["severity"],
                    "file": f["file"],
                    "ln": str(f["line"]),
                })
                all_findings.append(toon)

        self.logger.info(f"Findings from secret detector: {all_findings}")

        return {
            "secrets": all_findings,
        }
