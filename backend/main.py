from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import time
from graph.workflow import scan_workflow

app = FastAPI(
    title="ShipSafe API",
    description="AI-powered security vulnerability scanning platform",
    version="1.0.0"
)


class ScanRequest(BaseModel):
    """Request model for initiating a repository scan."""
    repo_url: str


class ScanResponse(BaseModel):
    """Response model for scan results."""
    success: bool
    data: dict | None = None
    error: str | None = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ShipSafe API",
        "version": "1.0.0",
        "endpoints": {
            "scan": "POST /api/scan",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/scan", response_model=ScanResponse)
async def scan_repository(request: ScanRequest):
    """
    Initiate a security vulnerability scan for a GitHub repository.
    
    Args:
        request: ScanRequest containing repo_url
        
    Returns:
        ScanResponse with scan results or error message
    """
    try:
        # Validate repo URL
        if not request.repo_url:
            raise HTTPException(
                status_code=400,
                detail="repo_url is required"
            )
        
        # Initialize state
        start_time = time.time()
        initial_state = {
            "repo_url": request.repo_url,
            "repo_metadata": {},
            "vulnerabilities": [],
            "secrets": [],
            "enriched_vulnerabilities": [],
            "enriched_secrets": [],
            "vulnerability_patches": [],
            "secret_patches": [],
            "final_report": None,
            "errors": [],
            "status": "pending",
            "agent_trace": [],
            "execution_time": 0.0,
        }
        
        # Execute the workflow
        result = await scan_workflow.ainvoke(initial_state)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Build final report from state
        final_report = {
            "scan_summary": {
                "total_issues": len(result.get("vulnerability_patches", [])) + len(result.get("secret_patches", [])),
                "vulnerabilities_count": len(result.get("vulnerability_patches", [])),
                "secrets_count": len(result.get("secret_patches", [])),
            },
            "repository": result.get("repo_metadata", {}),
            "vulnerabilities": result.get("vulnerability_patches", []),
            "secrets": result.get("secret_patches", []),
            "metadata": {
                "agents_invoked": result.get("agent_trace", []),
                "errors": result.get("errors", []),
                "status": result.get("status", "completed"),
                "execution_time": execution_time,
            },
        }
        
        return ScanResponse(
            success=True,
            data=final_report
        )
        
    except Exception as e:
        return ScanResponse(
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)