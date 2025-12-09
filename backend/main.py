import os
import sys
import time
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
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

# In-memory progress tracking (use Redis in production)
scan_progress: Dict[str, Dict[str, Any]] = {}


class ScanRequest(BaseModel):
    """Request model for initiating a repository scan."""
    repo_url: str


class ScanResponse(BaseModel):
    """Response model for scan results."""
    success: bool
    data: dict | None = None
    error: str | None = None


class ScanStartResponse(BaseModel):
    """Response model for scan initiation."""
    success: bool
    scan_id: str | None = None
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


@app.get("/api/scan/status/{scan_id}")
async def get_scan_status(scan_id: str):
    """
    Get the current status of a scan.
    
    Args:
        scan_id: Unique scan identifier
        
    Returns:
        Current scan progress and status
    """
    if scan_id not in scan_progress:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_progress[scan_id]


async def run_scan_workflow(scan_id: str, repo_url: str, github_token: str):
    """
    Background task to run the scan workflow.
    
    Args:
        scan_id: Unique scan identifier  
        repo_url: Repository URL to scan
        github_token: GitHub access token
    """
    start_time = time.time()
    
    try:
        # Progress callback function
        def update_progress(agent_name: str, status: str, details: dict = None):
            if scan_id in scan_progress:
                scan_progress[scan_id]["current_agent"] = agent_name
                scan_progress[scan_id]["agents"][agent_name]["status"] = status
                
                if status == "in_progress":
                    scan_progress[scan_id]["agents"][agent_name]["started_at"] = datetime.now().isoformat()
                elif status == "completed":
                    scan_progress[scan_id]["agents"][agent_name]["completed_at"] = datetime.now().isoformat()
                    
                if details:
                    scan_progress[scan_id]["agents"][agent_name].update(details)

        # Initialize state
        initial_state = {
            "repo_url": repo_url,
            "github_token": github_token,
            "scan_id": scan_id,
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
            "current_agent": None,
            "progress_callback": update_progress,
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
            "files": result.get("files", {}),
            "metadata": {
                "agents_invoked": result.get("agent_trace", []),
                "errors": result.get("errors", []),
                "status": result.get("status", "completed"),
                "execution_time": execution_time,
            },
        }
        
        # Update progress to completed with results
        scan_progress[scan_id]["status"] = "completed"
        scan_progress[scan_id]["completed_at"] = datetime.now().isoformat()
        scan_progress[scan_id]["results"] = final_report
        
    except Exception as e:
        # Update progress to error state
        if scan_id in scan_progress:
            scan_progress[scan_id]["status"] = "error"
            scan_progress[scan_id]["error"] = str(e)
            scan_progress[scan_id]["completed_at"] = datetime.now().isoformat()


@app.post("/api/scan", response_model=ScanStartResponse)
async def scan_repository(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Initiate a security vulnerability scan for a GitHub repository.
    
    Args:
        request: ScanRequest containing repo_url
        background_tasks: FastAPI background tasks
        
    Returns:
        ScanStartResponse with scan_id for tracking
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

        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        scan_progress[scan_id] = {
            "scan_id": scan_id,
            "repo_url": request.repo_url,
            "status": "running",
            "current_agent": "orchestrator",
            "agents": {
                "orchestrator": {"status": "pending", "started_at": None, "completed_at": None},
                "code_scanner": {"status": "pending", "started_at": None, "completed_at": None},
                "secret_detector": {"status": "pending", "started_at": None, "completed_at": None},
                "context_enricher": {"status": "pending", "started_at": None, "completed_at": None},
                "remediation": {"status": "pending", "started_at": None, "completed_at": None},
            },
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "results": None,
        }
        
        # Run scan in background
        background_tasks.add_task(run_scan_workflow, scan_id, request.repo_url, github_token)
        
        return ScanStartResponse(
            success=True,
            scan_id=scan_id
        )
        
    except Exception as e:
        return ScanStartResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/scan/results/{scan_id}")
async def get_scan_results(scan_id: str):
    """
    Get the results of a completed scan.
    
    Args:
        scan_id: Unique scan identifier
        
    Returns:
        Scan results if completed
    """
    if scan_id not in scan_progress:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    progress = scan_progress[scan_id]
    
    if progress["status"] == "running":
        return {
            "status": "running",
            "message": "Scan is still in progress"
        }
    elif progress["status"] == "error":
        return {
            "status": "error",
            "error": progress.get("error", "Unknown error occurred")
        }
    elif progress["status"] == "completed":
        return {
            "status": "completed",
            "data": progress.get("results")
        }
    
    return {"status": "unknown"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)