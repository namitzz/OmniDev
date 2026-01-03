"""
Task Runner - Orchestrates Agent Execution

Coordinates the execution of multiple agents to complete a task.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from ..core.models import Task, TaskStatus, AgentExecution, TaskMetrics, AgentType
from ..core.database import get_db
from ..core.logging import TaskLogger
from ..agents import PlannerAgent, FeatureDevAgent, TesterAgent, RefactorAgent, ReviewerAgent, AgentInput
from ..git import GitHubClient, GitOperations
from ..rag import RepositoryIndexer
from ..policies import PolicyEngine
from sqlalchemy import select

import uuid


class TaskRunner:
    """
    Orchestrates the execution of agents to complete development tasks.
    
    Workflow:
    1. PlannerAgent creates implementation plan
    2. FeatureDevAgent implements changes
    3. TesterAgent creates tests
    4. RefactorAgent improves code quality
    5. ReviewerAgent performs final review
    """
    
    def __init__(self):
        self.github = GitHubClient()
        self.git_ops = GitOperations()
        self.policy_engine = PolicyEngine()
        
        # Initialize agents
        self.planner = PlannerAgent()
        self.feature_dev = FeatureDevAgent()
        self.tester = TesterAgent()
        self.refactor = RefactorAgent()
        self.reviewer = ReviewerAgent()
        
        self.logger = None  # Set per task
    
    async def run_task(self, issue_number: int) -> Dict[str, Any]:
        """
        Execute a task from a GitHub issue
        
        Returns:
            Task execution results
        """
        # Create task record
        task_id = str(uuid.uuid4())
        self.logger = TaskLogger(task_id, "TaskRunner")
        
        self.logger.info("Task execution started", issue_number=issue_number)
        
        try:
            # Get issue from GitHub
            issue = self.github.get_issue(issue_number)
            
            # Create task in database
            async with get_db() as db:
                task = Task(
                    id=task_id,
                    github_issue_number=issue_number,
                    title=issue["title"],
                    description=issue["body"],
                    status=TaskStatus.IN_PROGRESS,
                    started_at=datetime.utcnow(),
                    policies=self.policy_engine.get_policy_summary()
                )
                db.add(task)
                await db.commit()
            
            # Prepare repository context
            repo_context = await self._prepare_repo_context(issue)
            
            # Execute workflow
            result = await self._execute_workflow(task_id, issue, repo_context)
            
            # Update task record
            async with get_db() as db:
                stmt = select(Task).where(Task.id == task_id)
                result_task = await db.execute(stmt)
                task = result_task.scalar_one()
                
                task.status = TaskStatus.COMPLETED if result["success"] else TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.success = result["success"]
                task.error_message = result.get("error")
                
                await db.commit()
            
            self.logger.task_complete(success=result["success"])
            
            return result
        
        except Exception as e:
            self.logger.error("Task execution failed", error=str(e))
            
            # Update task as failed
            async with get_db() as db:
                stmt = select(Task).where(Task.id == task_id)
                result_task = await db.execute(stmt)
                task = result_task.scalar_one_or_none()
                
                if task:
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.utcnow()
                    task.success = False
                    task.error_message = str(e)
                    await db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    async def _prepare_repo_context(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare repository context for agents"""
        self.logger.info("Preparing repository context")
        
        # Get repository information
        languages = self.github.get_repository_languages()
        primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown"
        
        # Index repository (if not already done)
        # For production, this would be done asynchronously
        # indexer = RepositoryIndexer("./workspace")
        # indexer.index_repository()
        
        context = {
            "repository": f"{self.github.repo.full_name}",
            "primary_language": primary_language,
            "languages": languages,
            "issue_number": issue["number"],
            "issue_description": issue["body"],
            "issue_title": issue["title"],
            "issue_labels": issue["labels"],
        }
        
        return context
    
    async def _execute_workflow(
        self,
        task_id: str,
        issue: Dict[str, Any],
        repo_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the agent workflow"""
        
        workflow_result = {
            "success": True,
            "task_id": task_id,
            "stages": {}
        }
        
        # Stage 1: Planning
        self.logger.info("Stage 1: Planning")
        plan_result = await self._run_planner(task_id, repo_context)
        workflow_result["stages"]["planning"] = plan_result
        
        if not plan_result["success"]:
            workflow_result["success"] = False
            workflow_result["error"] = "Planning stage failed"
            return workflow_result
        
        plan = plan_result["output"]["plan"]
        
        # Stage 2: Feature Development
        self.logger.info("Stage 2: Feature Development")
        dev_result = await self._run_feature_dev(task_id, repo_context, plan)
        workflow_result["stages"]["development"] = dev_result
        
        if not dev_result["success"]:
            workflow_result["success"] = False
            workflow_result["error"] = "Development stage failed"
            return workflow_result
        
        implementation = dev_result["output"]["implementation"]
        
        # Stage 3: Testing
        self.logger.info("Stage 3: Testing")
        test_result = await self._run_tester(task_id, repo_context, implementation)
        workflow_result["stages"]["testing"] = test_result
        
        if not test_result["success"]:
            # Testing failures are warnings, not blockers
            self.logger.warning("Testing stage had issues")
        
        # Stage 4: Code Review
        self.logger.info("Stage 4: Code Review")
        review_result = await self._run_reviewer(task_id, repo_context, implementation, test_result.get("output"))
        workflow_result["stages"]["review"] = review_result
        
        if not review_result["success"]:
            workflow_result["success"] = False
            workflow_result["error"] = "Review stage failed"
            return workflow_result
        
        review = review_result["output"]["review"]
        
        # Check if approved
        if not review.get("approved", False):
            workflow_result["success"] = False
            workflow_result["error"] = "Code review not approved"
            workflow_result["review_issues"] = review.get("issues", [])
        
        return workflow_result
    
    async def _run_planner(self, task_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run PlannerAgent"""
        agent_input = AgentInput(
            task_id=task_id,
            context=context,
            policies=self.policy_engine.policies
        )
        
        output = await self.planner.execute(agent_input)
        
        # Save execution record
        await self._save_agent_execution(task_id, AgentType.PLANNER, agent_input, output)
        
        return {
            "success": output.success,
            "output": output.result,
            "error": output.error
        }
    
    async def _run_feature_dev(
        self,
        task_id: str,
        context: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run FeatureDevAgent"""
        # Add plan to context
        context["plan"] = plan
        context["current_subtask"] = plan["subtasks"][0] if plan.get("subtasks") else {}
        
        agent_input = AgentInput(
            task_id=task_id,
            context=context,
            policies=self.policy_engine.policies
        )
        
        output = await self.feature_dev.execute(agent_input)
        
        # Save execution record
        await self._save_agent_execution(task_id, AgentType.FEATURE_DEV, agent_input, output)
        
        return {
            "success": output.success,
            "output": output.result,
            "error": output.error
        }
    
    async def _run_tester(
        self,
        task_id: str,
        context: Dict[str, Any],
        implementation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run TesterAgent"""
        context["implementation"] = implementation
        
        agent_input = AgentInput(
            task_id=task_id,
            context=context,
            policies=self.policy_engine.policies
        )
        
        output = await self.tester.execute(agent_input)
        
        # Save execution record
        await self._save_agent_execution(task_id, AgentType.TESTER, agent_input, output)
        
        return {
            "success": output.success,
            "output": output.result,
            "error": output.error
        }
    
    async def _run_reviewer(
        self,
        task_id: str,
        context: Dict[str, Any],
        implementation: Dict[str, Any],
        test_results: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run ReviewerAgent"""
        context["implementation_summary"] = implementation.get("summary", "")
        context["changes"] = implementation.get("changes", [])
        context["test_results"] = test_results.get("tests", {}) if test_results else {}
        
        agent_input = AgentInput(
            task_id=task_id,
            context=context,
            policies=self.policy_engine.policies
        )
        
        output = await self.reviewer.execute(agent_input)
        
        # Save execution record
        await self._save_agent_execution(task_id, AgentType.REVIEWER, agent_input, output)
        
        return {
            "success": output.success,
            "output": output.result,
            "error": output.error
        }
    
    async def _save_agent_execution(
        self,
        task_id: str,
        agent_type: AgentType,
        input_data: AgentInput,
        output: Any
    ):
        """Save agent execution to database"""
        async with get_db() as db:
            execution = AgentExecution(
                task_id=task_id,
                agent_type=agent_type,
                completed_at=datetime.utcnow(),
                status=TaskStatus.COMPLETED if output.success else TaskStatus.FAILED,
                input_context=input_data.context,
                output_result=output.result,
                error_message=output.error,
                total_tokens=output.tokens_used,
                estimated_cost=output.estimated_cost,
                model_name=self.policy_engine.policies.get(f"{agent_type.value}_model", "gpt-4-turbo-preview")
            )
            db.add(execution)
            await db.commit()
