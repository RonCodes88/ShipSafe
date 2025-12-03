"""Code Scanning Agent - Vulnerability detection and pattern analysis."""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import to_toon
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from utils.tree_parser import extract_functions, get_language_parser


tokenizer = AutoTokenizer.from_pretrained('mrm8488/codebert-base-finetuned-detect-insecure-code')
model = AutoModelForSequenceClassification.from_pretrained('mrm8488/codebert-base-finetuned-detect-insecure-code')

class CodeScannerAgent(BaseAgent):

    async def predict_defect(code_snippet: str):
        inputs = tokenizer(
            code_snippet,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=512
        )

        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=1)
            insecure_prob = probs[0][1].item()

        return insecure_prob


    async def _execute(self, state: ScanState) -> Dict[str, Any]:
        repo_name = state["repo_metadata"].get("name", "unknown")
        self.logger.info(f"Scanning code for vulnerabilities in: {repo_name}")

        vulnerabilities = []

        for f in state["repo_metadata"]["files"]:
            path = f["path"]
            code = f["content"]
            ext = path.split(".")[-1]

            parser = get_language_parser(ext)
            units = extract_functions(code, parser, ext)

            for u in units:
                score = await self.predict_defect(u["code"])

                if score > 0.55:
                    severity = "HIGH" if score > 0.8 else "MEDIUM"

                    vuln = to_toon({
                        "vuln": "ML_DEFECT",
                        "sev": severity,
                        "file": path,
                        "ln": f"{u['start']}-{u['end']}",
                        "prob": round(score, 3),
                        "type": u["type"]
                    })

                    vulnerabilities.append(vuln)

        state["vulnerabilities"] += vulnerabilities
        state["agent_trace"].append("code_scanner")

        return {
            "vulnerabilities": vulnerabilities,
            "status": "code_scan_complete",
        }
