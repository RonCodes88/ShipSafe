"""LangGraph workflow definition for vulnerability scanning."""

from langgraph.graph import StateGraph, END
from .state import ScanState



def create_scan_workflow():
    
    """
    Create the vulnerability scanning workflow using LangGraph.
    
    Workflow follows sequential flow:
    START → Orchestrator → Code Scanner → Context Enrichment → Remediation 
    → Secret Detector → Context Enrichment (reuse) → Remediation (reuse) → END
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the state graph
    from backend.agents.orchestrator import OrchestratorAgent
    from backend.agents.code_scanner import CodeScannerAgent
    from backend.agents.secret_detector import SecretDetectorAgent
    from backend.agents.context_enricher import ContextEnricherAgent
    from backend.agents.remediation import RemediationAgent


    # Initialize agents
    orchestrator = OrchestratorAgent()
    code_scanner = CodeScannerAgent()
    secret_detector = SecretDetectorAgent()
    context_enricher = ContextEnricherAgent()
    remediation = RemediationAgent()


    async def orchestrator_node(state: ScanState) -> ScanState:
        """Orchestrator agent node."""
        return await orchestrator.process(state)


    async def code_scanner_node(state: ScanState) -> ScanState:
        """Code scanning agent node."""
        return await code_scanner.process(state)


    async def secret_detector_node(state: ScanState) -> ScanState:
        """Secret detection agent node."""
        return await secret_detector.process(state)


    async def context_enricher_node(state: ScanState) -> ScanState:
        """Context enrichment agent node."""
        return await context_enricher.process(state)


    async def remediation_node(state: ScanState) -> ScanState:
        """Remediation agent node."""
        return await remediation.process(state)
    
    workflow = StateGraph(ScanState)
    
    # Add all agent nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("code_scanner", code_scanner_node)
    workflow.add_node("secret_detector", secret_detector_node)
    workflow.add_node("context_enricher", context_enricher_node)
    workflow.add_node("remediation", remediation_node)
    
    # Set entry point
    workflow.set_entry_point("orchestrator")
    
    # Add edges for sequential flow
    # Phase 1: Code vulnerability scanning pipeline
    workflow.add_edge("orchestrator", "code_scanner")
    workflow.add_edge("code_scanner", "context_enricher")
    workflow.add_edge("context_enricher", "remediation")
    
    # Phase 2: Secret detection pipeline
    workflow.add_edge("remediation", "secret_detector")
    # Context enricher and remediation are reused for secrets
    # In LangGraph, nodes can be revisited in the same execution
    workflow.add_edge("secret_detector", "context_enricher")
    workflow.add_edge("context_enricher", "remediation")
    
    # End after final remediation
    workflow.add_edge("remediation", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Create the workflow instance
scan_workflow = create_scan_workflow()

