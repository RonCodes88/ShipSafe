"""
Fast Secret Detection Agent:
Runs regex + entropy + base64 locally,
then sends only candidates to the LLM for classification.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import to_toon

import base64
import re
import math
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from langchain_ollama import ChatOllama


# ============================
# Utility functions
# ============================

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {c: s.count(c) for c in set(s)}
    return -sum((count/len(s)) * math.log2(count/len(s)) for count in freq.values())


def try_base64_decode(value: str) -> str:
    """Return decoded Base64 string or None."""
    try:
        padded = value + "=" * (-len(value) % 4)
        decoded = base64.b64decode(padded, validate=True)
        return decoded.decode("utf-8", errors="replace")
    except Exception:
        return None


# ============================
# Models
# ============================

class SecretFinding(BaseModel):
    secret_value: str
    secret_type: str
    file: str
    line: int
    severity: str


class SecretDetectorAgent(BaseAgent):

    def __init__(self, config: AgentConfig = None):
        super().__init__(config)

        self.llm = ChatOllama(
            model="llama3",
            temperature=0
        )

    def extract_candidates(self, content: str):
        lines = content.split("\n")
        candidates = []

        # Regexes for typical secrets
        regex_patterns = {
            "AWS_ACCESS_KEY": r"AKIA[0-9A-Z]{16}",
            "GITHUB_TOKEN": r"gh[pousr]_[A-Za-z0-9]{36}",
            "SLACK_TOKEN": r"xox[baprs]-[A-Za-z0-9-]{10,48}",
            "GENERIC_KEY": r"[A-Za-z0-9/\+=]{20,}"  # long suspicious strings
        }

        for i, line in enumerate(lines, start=1):

            # Regex detections
            for name, pattern in regex_patterns.items():
                for match in re.findall(pattern, line):
                    candidates.append({
                        "value": match,
                        "line": i,
                        "origin": name,
                        "decoded": None,
                        "entropy": shannon_entropy(match)
                    })

            # Entropy-based detection
            tokens = re.findall(r"[A-Za-z0-9/\+=]{20,}", line)
            for tok in tokens:
                ent = shannon_entropy(tok)
                if ent > 3.5:
                    candidates.append({
                        "value": tok,
                        "line": i,
                        "origin": "high_entropy",
                        "decoded": None,
                        "entropy": ent
                    })

            # Base64 detection
            tokens = re.findall(r"[A-Za-z0-9/\+=]{12,}", line)
            for tok in tokens:
                decoded = try_base64_decode(tok)
                if decoded and len(decoded) > 6:
                    candidates.append({
                        "value": tok,
                        "line": i,
                        "origin": "base64",
                        "decoded": decoded,
                        "entropy": shannon_entropy(decoded)
                    })

        return candidates

    # ============================
    # LLM Classification
    # ============================
    async def classify_candidates(self, file_path: str, candidates: List[dict]):

        if not candidates:
            return []

        prompt = f"""
You are ShipSafe Secret Classifier.

Below are candidate secrets extracted from local detection
(regex, entropy, base64 decode). Classify each item.

Return a JSON list of:

{{
  "secret_value": string,
  "secret_type": string,
  "file": string,
  "line": number,
  "severity": string
}}

Do not add extra text.

FILE: {file_path}

CANDIDATES:
{candidates}
"""

        try:
            response = await self.llm.ainvoke(prompt)
            print(response.content)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM error: {e}")
            return []

    async def _execute(self, state: ScanState) -> Dict[str, Any]:

        repo_files = state.get("repo_metadata", {}).get("files", [])
        all_findings = []

        for fileinfo in repo_files:
            path = fileinfo["path"]
            content = fileinfo.get("content", "")

            # Step 1: Fast local candidate extraction
            candidates = self.extract_candidates(content)
            print(candidates)

            # Step 2: LLM classification (fast single call)
            findings = await self.classify_candidates(path, candidates)

            # Step 3: Convert to TOON
            if isinstance(findings, list):
                for f in findings:
                    toon = to_toon({
                        "secret": f.get("secret_value", "")[:30] + "...",
                        "type": f.get("secret_type", "unknown"),
                        "sev": f.get("severity", "HIGH"),
                        "file": f.get("file", path),
                        "ln": str(f.get("line", 0)),
                    })
                    all_findings.append(toon)
            print(all_findings)

        return {
            "secrets": all_findings,
            "status": "secret_scan_complete_fast"
        }
