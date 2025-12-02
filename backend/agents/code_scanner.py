"""Code Scanning Agent - Vulnerability detection and pattern analysis."""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentConfig
from graph.state import ScanState
from utils.toon_parser import to_toon
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch
from utils.tree_parser import extract_functions, get_language_parser

tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
codebert_model = RobertaForSequenceClassification.from_pretrained(
    "microsoft/codebert-base", num_labels=2
)
codebert_model.eval()

class CodeScannerAgent(BaseAgent):

    async def predict_defect(self, code: str) -> float:
        inputs = tokenizer(
            code,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        with torch.no_grad():
            logits = codebert_model(**inputs).logits
            probs = torch.softmax(logits, dim=1)

        return probs[0][1].item()


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

        # Append instead of overwrite
        state["vulnerabilities"] += vulnerabilities
        state["agent_trace"].append("code_scanner")

        return {
            "vulnerabilities": vulnerabilities,
            "status": "code_scan_complete",
        }
