"""LangGraph state schema for vulnerability scanning workflow."""

from typing import TypedDict, Optional


class ScanState(TypedDict):
    """
    Shared state object that flows through all agents in the scanning workflow.
    
    Uses TOON (Token-Oriented Object Notation) format for inter-agent communication
    to reduce token usage.
    """
    # Input
    repo_url: str
    repo_metadata: dict
    
    # Code Scanning Pipeline
    vulnerabilities: list[str]  # TOON format from Code Scanning Agent
    enriched_vulnerabilities: list[str]  # TOON format from Context Enrichment
    vulnerability_patches: list[str]  # TOON format from Remediation Agent
    
    # Secret Detection Pipeline
    secrets: list[str]  # TOON format from Secret Detection Agent
    enriched_secrets: list[str]  # TOON format from Context Enrichment
    secret_patches: list[str]  # TOON format from Remediation Agent
    
    # Aggregated Results
    final_report: Optional[dict]  # JSON format from Response Aggregator
    
    # Metadata
    errors: list[str]
    status: str
    agent_trace: list[str]  # Track which agents were invoked
    execution_time: float

