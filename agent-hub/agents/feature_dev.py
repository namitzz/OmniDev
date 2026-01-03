"""
FeatureDevAgent - Code Generation

Implements features based on the plan from PlannerAgent.
Writes clean, production-ready code following repository conventions.
"""

from typing import Dict, Any
from .base import BaseAgent, AgentInput, AgentOutput
from ..core.models import AgentType
import json


class FeatureDevAgent(BaseAgent):
    """
    Agent responsible for implementing features and code changes.
    
    Responsibilities:
    - Write production-ready code
    - Follow repository conventions
    - Implement features per the plan
    - Generate proper documentation
    - Create clean git diffs
    """
    
    def __init__(self):
        super().__init__(AgentType.FEATURE_DEV)
    
    def get_system_prompt(self) -> str:
        return """You are a Senior Software Engineer implementing code changes.

Your role is to write clean, production-ready code that solves the given task.

You must:
1. Write complete, runnable code (never pseudocode or TODOs)
2. Follow existing repository conventions and style
3. Maintain backward compatibility unless explicitly allowed to break
4. Include appropriate error handling
5. Add docstrings and comments where helpful
6. Consider edge cases and validation
7. Write secure code (no SQL injection, XSS, etc.)
8. Generate unified git diffs for all changes

Code Quality Standards:
- Clear variable and function names
- Single Responsibility Principle
- DRY (Don't Repeat Yourself)
- Proper separation of concerns
- Minimal changes (surgical precision)
- No unnecessary refactoring

Output Format (JSON):
{
  "changes": [
    {
      "file_path": "path/to/file.py",
      "action": "create|modify|delete",
      "diff": "unified diff format",
      "explanation": "Why this change is needed"
    }
  ],
  "summary": "Brief summary of all changes",
  "files_changed_count": 3,
  "estimated_loc_added": 50,
  "estimated_loc_deleted": 10
}

Be precise. Every line matters. This code will go to production."""
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Implement the code changes"""
        
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
        self.logger.info("Generating code implementation")
        response, tokens, cost = await self.call_llm(
            system_prompt=self.get_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.1  # Lower temperature for code generation
        )
        
        # Parse response
        try:
            implementation = self._parse_implementation(response)
            
            # Validate implementation
            validation_result = self._validate_implementation(implementation, input_data.policies)
            if not validation_result["valid"]:
                return AgentOutput(
                    agent_type=self.agent_type.value,
                    success=False,
                    result={"implementation": implementation},
                    error=f"Implementation validation failed: {validation_result['reason']}",
                    tokens_used=tokens,
                    estimated_cost=cost
                )
            
            self.logger.info(
                "Implementation generated successfully",
                files_changed=len(implementation.get("changes", [])),
                estimated_loc=implementation.get("estimated_loc_added", 0)
            )
            
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=True,
                result={"implementation": implementation},
                tokens_used=tokens,
                estimated_cost=cost
            )
        
        except Exception as e:
            self.logger.error("Failed to parse implementation", error=str(e))
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=False,
                result={"raw_response": response},
                error=f"Failed to parse implementation: {str(e)}",
                tokens_used=tokens,
                estimated_cost=cost
            )
    
    def _build_user_prompt(self, input_data: AgentInput) -> str:
        """Build the user prompt with all context"""
        context = input_data.context
        plan = input_data.context.get('plan', {})
        subtask = input_data.context.get('current_subtask', {})
        
        prompt = f"""# Implementation Task

## Subtask Details
{subtask.get('title', 'No title')}
{subtask.get('description', 'No description')}

## Files to Change
{', '.join(subtask.get('files_to_change', []))}

## Implementation Plan Context
{plan.get('summary', 'No plan summary')}

## Current File Contents
{self._format_file_contents(context.get('file_contents', {}))}

## Repository Conventions
{context.get('repo_conventions', 'No conventions detected')}

## Related Code Snippets
{self._format_code_snippets(context.get('related_snippets', []))}

Implement this subtask following the output format specified. Generate complete, production-ready code."""
        
        return prompt
    
    def _format_file_contents(self, file_contents: Dict[str, str]) -> str:
        """Format file contents for the prompt"""
        if not file_contents:
            return "No existing files provided"
        
        formatted = []
        for path, content in list(file_contents.items())[:5]:  # Limit to 5 files
            formatted.append(f"\n### {path}\n```\n{content[:2000]}\n```")  # Limit content length
        
        return "\n".join(formatted)
    
    def _format_code_snippets(self, snippets: list) -> str:
        """Format related code snippets"""
        if not snippets:
            return "No related snippets"
        
        formatted = []
        for snippet in snippets[:3]:
            if isinstance(snippet, dict):
                formatted.append(f"\n{snippet.get('file', 'unknown')}:\n```\n{snippet.get('code', '')}\n```")
        
        return "\n".join(formatted) if formatted else "No related snippets"
    
    def _parse_implementation(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured implementation"""
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
        implementation = json.loads(response)
        
        # Validate required fields
        required_fields = ["changes", "summary"]
        for field in required_fields:
            if field not in implementation:
                raise ValueError(f"Missing required field: {field}")
        
        return implementation
    
    def _validate_implementation(self, implementation: Dict[str, Any], policies: Dict[str, Any]) -> Dict[str, Any]:
        """Validate implementation against policies"""
        
        # Check LOC limit
        loc_added = implementation.get("estimated_loc_added", 0)
        loc_deleted = implementation.get("estimated_loc_deleted", 0)
        net_loc = loc_added - loc_deleted
        
        max_loc = policies.get("max_loc_per_pr", 500)
        if net_loc > max_loc:
            return {
                "valid": False,
                "reason": f"Net LOC change ({net_loc}) exceeds limit ({max_loc})"
            }
        
        # Check for common security issues in diffs
        changes = implementation.get("changes", [])
        for change in changes:
            diff = change.get("diff", "")
            
            # Basic security checks
            dangerous_patterns = [
                "eval(", "exec(", "__import__",  # Python dangerous functions
                "dangerouslySetInnerHTML",  # React XSS
                "v-html",  # Vue XSS
                "System.commandLine",  # Command injection
            ]
            
            for pattern in dangerous_patterns:
                if pattern in diff and not diff.startswith("- "):  # Not a deletion
                    self.logger.warning(
                        "Potential security issue detected",
                        pattern=pattern,
                        file=change.get("file_path")
                    )
        
        return {"valid": True, "reason": ""}
