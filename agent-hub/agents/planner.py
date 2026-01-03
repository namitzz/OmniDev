"""
PlannerAgent - Tech Lead Reasoning

Analyzes issues and creates detailed implementation plans.
Acts as the tech lead, breaking down work and identifying dependencies.
"""

from typing import Dict, Any
from .base import BaseAgent, AgentInput, AgentOutput
from ..core.models import AgentType
import json


class PlannerAgent(BaseAgent):
    """
    Agent responsible for planning and breaking down tasks.
    
    Responsibilities:
    - Analyze issue requirements
    - Break down into subtasks
    - Identify file changes needed
    - Determine test strategy
    - Flag risks and dependencies
    """
    
    def __init__(self):
        super().__init__(AgentType.PLANNER)
    
    def get_system_prompt(self) -> str:
        return """You are a Senior Tech Lead responsible for planning software implementations.

Your role is to analyze issues/tickets and create detailed, actionable implementation plans.

You must:
1. Thoroughly understand the requirements
2. Break down the work into clear subtasks
3. Identify which files need to be created or modified
4. Determine the test strategy
5. Flag any risks, dependencies, or blockers
6. Estimate complexity
7. Recommend which agents should handle each subtask

Consider:
- Repository conventions and existing patterns
- Code architecture and separation of concerns
- Testing requirements and coverage
- Security implications
- Performance considerations
- Breaking change risks

Output your plan as structured JSON with:
{
  "summary": "Brief overview of what needs to be done",
  "subtasks": [
    {
      "id": "subtask-1",
      "title": "Title of subtask",
      "description": "Detailed description",
      "files_to_change": ["file1.py", "file2.py"],
      "agent": "feature_dev|refactor|tester",
      "dependencies": ["subtask-0"],
      "estimated_complexity": "low|medium|high"
    }
  ],
  "test_strategy": {
    "unit_tests": "Description of unit tests needed",
    "integration_tests": "Description of integration tests needed",
    "coverage_target": 85
  },
  "risks": [
    {
      "risk": "Description of risk",
      "mitigation": "How to mitigate",
      "severity": "low|medium|high"
    }
  ],
  "requires_breaking_changes": false,
  "requires_new_dependencies": false
}

Be precise, thorough, and realistic. This plan will guide the entire implementation."""
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Create implementation plan for the task"""
        
        # Check if should abort
        should_abort, abort_reason = self.should_abort(input_data.context)
        if should_abort:
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=False,
                result={},
                error=f"Aborted: {abort_reason}"
            )
        
        # Build context for the LLM
        user_prompt = self._build_user_prompt(input_data)
        
        # Call LLM
        self.logger.info("Generating implementation plan")
        response, tokens, cost = await self.call_llm(
            system_prompt=self.get_system_prompt(),
            user_prompt=user_prompt
        )
        
        # Parse response
        try:
            plan = self._parse_plan(response)
            
            # Validate plan against policies
            validation_result = self._validate_plan(plan, input_data.policies)
            if not validation_result["valid"]:
                return AgentOutput(
                    agent_type=self.agent_type.value,
                    success=False,
                    result={"plan": plan},
                    error=f"Plan validation failed: {validation_result['reason']}",
                    tokens_used=tokens,
                    estimated_cost=cost
                )
            
            self.logger.info(
                "Plan generated successfully",
                subtasks_count=len(plan.get("subtasks", [])),
                requires_breaking_changes=plan.get("requires_breaking_changes", False)
            )
            
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=True,
                result={"plan": plan},
                tokens_used=tokens,
                estimated_cost=cost
            )
        
        except Exception as e:
            self.logger.error("Failed to parse plan", error=str(e))
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=False,
                result={"raw_response": response},
                error=f"Failed to parse plan: {str(e)}",
                tokens_used=tokens,
                estimated_cost=cost
            )
    
    def _build_user_prompt(self, input_data: AgentInput) -> str:
        """Build the user prompt with all context"""
        context = input_data.context
        policies = input_data.policies
        
        prompt = f"""# Task Details

## Issue Description
{context.get('issue_description', 'No description provided')}

## Issue Number
{context.get('issue_number', 'N/A')}

## Repository Context
Repository: {context.get('repository', 'N/A')}
Language: {context.get('primary_language', 'Unknown')}

## Relevant Files
{self._format_files(context.get('relevant_files', []))}

## Repository Conventions
{context.get('repo_conventions', 'No conventions detected')}

## Policies
- Max LOC per PR: {policies.get('max_loc_per_pr', 500)}
- Allow new dependencies: {policies.get('allow_new_deps', False)}
- Min test coverage: {policies.get('min_test_coverage', 80)}%
- Allow breaking changes: {policies.get('allow_breaking_changes', False)}

Create a detailed implementation plan following the specified JSON format."""
        
        return prompt
    
    def _format_files(self, files: list) -> str:
        """Format list of files for the prompt"""
        if not files:
            return "No specific files provided"
        
        formatted = []
        for file_info in files[:10]:  # Limit to 10 files to save tokens
            if isinstance(file_info, dict):
                path = file_info.get('path', 'unknown')
                summary = file_info.get('summary', 'No summary')
                formatted.append(f"- {path}: {summary}")
            else:
                formatted.append(f"- {file_info}")
        
        if len(files) > 10:
            formatted.append(f"... and {len(files) - 10} more files")
        
        return "\n".join(formatted)
    
    def _parse_plan(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured plan"""
        # Try to extract JSON from response
        # LLM might wrap it in markdown code blocks
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        # Parse JSON
        plan = json.loads(response)
        
        # Validate required fields
        required_fields = ["summary", "subtasks", "test_strategy"]
        for field in required_fields:
            if field not in plan:
                raise ValueError(f"Missing required field: {field}")
        
        return plan
    
    def _validate_plan(self, plan: Dict[str, Any], policies: Dict[str, Any]) -> Dict[str, Any]:
        """Validate plan against policies"""
        
        # Check breaking changes
        if plan.get("requires_breaking_changes", False):
            if not policies.get("allow_breaking_changes", False):
                return {
                    "valid": False,
                    "reason": "Plan requires breaking changes but policy forbids them"
                }
        
        # Check new dependencies
        if plan.get("requires_new_dependencies", False):
            if not policies.get("allow_new_deps", False):
                return {
                    "valid": False,
                    "reason": "Plan requires new dependencies but policy forbids them"
                }
        
        # Estimate total LOC change
        subtasks = plan.get("subtasks", [])
        high_complexity_count = sum(1 for task in subtasks if task.get("estimated_complexity") == "high")
        
        # Rough estimate: medium task = 50 LOC, high = 150 LOC
        estimated_loc = high_complexity_count * 150 + (len(subtasks) - high_complexity_count) * 50
        
        max_loc = policies.get("max_loc_per_pr", 500)
        if estimated_loc > max_loc:
            return {
                "valid": False,
                "reason": f"Estimated LOC ({estimated_loc}) exceeds limit ({max_loc})"
            }
        
        return {"valid": True, "reason": ""}
