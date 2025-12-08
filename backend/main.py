import os
import sys
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import httpx
from dotenv import load_dotenv

# Ensure project root is on sys.path so `backend.*` imports inside the
# workflow graph resolve correctly when running `python main.py` from
# the `backend/` directory.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Load environment variables from `backend/.env` (where this file lives)
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

from graph.workflow import create_scan_workflow

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

        # Load GitHub token from environment
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(
                status_code=500,
                detail="GITHUB_TOKEN environment variable is not set"
            )

        # Initialize state
        start_time = time.time()
        initial_state = {
            "repo_url": request.repo_url,
            "github_token": github_token,
            "files": {},
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
        async with httpx.AsyncClient() as client:
            workflow_app = create_scan_workflow(client)
            result = await workflow_app.ainvoke(initial_state)
        
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
            "files": result.get("files", {}),  # Include file contents
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