"""
OmniDev - FastAPI Application

Main API server for the AI development team system.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from .core import init_db, close_db, settings, get_logger
from .runners import TaskRunner
from .git import GitHubClient

logger = get_logger(__name__)


# Pydantic models for API
class TaskCreate(BaseModel):
    """Request to create a new task from an issue"""
    issue_number: int
    priority: Optional[str] = "normal"


class TaskResponse(BaseModel):
    """Response for task creation"""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response for task status query"""
    task_id: str
    status: str
    stages: Dict[str, Any]
    success: bool
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    database: str


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting OmniDev API", app_name=settings.app_name)
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OmniDev API")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=f"{settings.app_name} API",
    description="AI-Powered Autonomous Development Team",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.environment,
        database="connected"
    )


@app.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_request: TaskCreate,
    background_tasks: BackgroundTasks
):
    """
    Create a new task from a GitHub issue
    
    This will start the agent workflow in the background.
    """
    try:
        logger.info("Creating task", issue_number=task_request.issue_number)
        
        # Create task runner
        runner = TaskRunner()
        
        # Run task in background
        background_tasks.add_task(runner.run_task, task_request.issue_number)
        
        return TaskResponse(
            task_id="pending",
            status="queued",
            message=f"Task created for issue #{task_request.issue_number}"
        )
    
    except Exception as e:
        logger.error("Failed to create task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    try:
        # TODO: Query database for task status
        return {
            "task_id": task_id,
            "status": "in_progress",
            "message": "Task status endpoint - implementation pending"
        }
    except Exception as e:
        logger.error("Failed to get task status", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks", response_model=Dict[str, Any])
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all tasks"""
    try:
        # TODO: Query database for tasks
        return {
            "tasks": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error("Failed to list tasks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/{task_id}/retry")
async def retry_task(task_id: str, background_tasks: BackgroundTasks):
    """Retry a failed task"""
    try:
        # TODO: Implement task retry logic
        return {
            "task_id": task_id,
            "status": "queued",
            "message": "Task retry queued"
        }
    except Exception as e:
        logger.error("Failed to retry task", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    try:
        # TODO: Implement task cancellation
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancelled"
        }
    except Exception as e:
        logger.error("Failed to cancel task", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents", response_model=Dict[str, Any])
async def list_agents():
    """List all available agents"""
    return {
        "agents": [
            {
                "type": "planner",
                "name": "PlannerAgent",
                "description": "Tech lead planning and task breakdown"
            },
            {
                "type": "feature_dev",
                "name": "FeatureDevAgent",
                "description": "Code implementation"
            },
            {
                "type": "tester",
                "name": "TesterAgent",
                "description": "Test generation and execution"
            },
            {
                "type": "refactor",
                "name": "RefactorAgent",
                "description": "Code quality and refactoring"
            },
            {
                "type": "reviewer",
                "name": "ReviewerAgent",
                "description": "Code review and security analysis"
            }
        ]
    }


@app.get("/policies", response_model=Dict[str, Any])
async def get_policies():
    """Get current policy configuration"""
    return {
        "max_loc_per_pr": settings.max_loc_per_pr,
        "allow_new_deps": settings.allow_new_deps,
        "min_test_coverage": settings.min_test_coverage,
        "allow_breaking_changes": settings.allow_breaking_changes,
        "max_retry_attempts": settings.max_retry_attempts,
        "enable_static_analysis": settings.enable_static_analysis,
        "enable_security_scan": settings.enable_security_scan,
    }


@app.get("/metrics", response_model=Dict[str, Any])
async def get_metrics():
    """Get system metrics"""
    return {
        "total_tasks": 0,
        "completed_tasks": 0,
        "failed_tasks": 0,
        "total_cost": 0.0,
        "total_tokens": 0,
        "uptime_seconds": 0
    }


@app.post("/webhook/github")
async def github_webhook(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    GitHub webhook endpoint
    
    Receives events from GitHub (issue created, PR opened, etc.)
    """
    try:
        event_type = payload.get("action")
        
        if event_type == "opened" and "issue" in payload:
            # New issue created, create task
            issue_number = payload["issue"]["number"]
            logger.info("GitHub webhook: issue opened", issue_number=issue_number)
            
            runner = TaskRunner()
            background_tasks.add_task(runner.run_task, issue_number)
            
            return {"message": "Task created from issue", "issue_number": issue_number}
        
        return {"message": "Event received", "type": event_type}
    
    except Exception as e:
        logger.error("Webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn agent-hub.main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.environment == "development"
    )
