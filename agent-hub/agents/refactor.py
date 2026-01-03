"""
RefactorAgent - Code Cleanup and Performance

Improves code quality, performance, and maintainability.
Refactors code while preserving functionality.
"""

from typing import Dict, Any
from .base import BaseAgent, AgentInput, AgentOutput
from ..core.models import AgentType
import json


class RefactorAgent(BaseAgent):
    """
    Agent responsible for code refactoring and optimization.
    
    Responsibilities:
    - Improve code structure and readability
    - Optimize performance bottlenecks
    - Reduce code duplication (DRY)
    - Apply design patterns appropriately
    - Maintain backward compatibility
    """
    
    def __init__(self):
        super().__init__(AgentType.REFACTOR)
    
    def get_system_prompt(self) -> str:
        return """You are a Senior Software Architect specializing in code refactoring.

Your role is to improve code quality while maintaining functionality.

You must:
1. Identify code smells and anti-patterns
2. Improve code structure and organization
3. Reduce duplication (DRY principle)
4. Enhance readability and maintainability
5. Optimize performance where beneficial
6. Apply appropriate design patterns
7. Maintain backward compatibility
8. Keep changes focused and minimal

Refactoring Principles:
- Small, incremental improvements
- One refactoring concern at a time
- Preserve all functionality
- Improve without over-engineering
- Clear naming and structure
- Better separation of concerns

Red Flags to Avoid:
- Breaking existing functionality
- Introducing new dependencies unnecessarily
- Over-abstraction
- Premature optimization
- Changing too much at once

Output Format (JSON):
{
  "refactorings": [
    {
      "file_path": "path/to/file.py",
      "type": "extract_method|rename|simplify|optimize|consolidate",
      "description": "What is being refactored and why",
      "diff": "unified diff format",
      "before_snippet": "relevant code before",
      "after_snippet": "relevant code after",
      "benefits": "Why this refactoring improves the code"
    }
  ],
  "summary": "Overall refactoring summary",
  "complexity_improvement": "high|medium|low",
  "performance_impact": "positive|neutral|negative"
}

Refactor thoughtfully. Every change should have a clear purpose."""
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Perform code refactoring"""
        
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
        self.logger.info("Performing refactoring analysis")
        response, tokens, cost = await self.call_llm(
            system_prompt=self.get_system_prompt(),
            user_prompt=user_prompt
        )
        
        # Parse response
        try:
            refactorings = self._parse_refactorings(response)
            
            # Validate refactorings
            validation_result = self._validate_refactorings(refactorings, input_data.policies)
            if not validation_result["valid"]:
                return AgentOutput(
                    agent_type=self.agent_type.value,
                    success=False,
                    result={"refactorings": refactorings},
                    error=f"Refactoring validation failed: {validation_result['reason']}",
                    tokens_used=tokens,
                    estimated_cost=cost
                )
            
            self.logger.info(
                "Refactoring completed successfully",
                refactoring_count=len(refactorings.get("refactorings", [])),
                complexity_improvement=refactorings.get("complexity_improvement", "unknown")
            )
            
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=True,
                result={"refactorings": refactorings},
                tokens_used=tokens,
                estimated_cost=cost
            )
        
        except Exception as e:
            self.logger.error("Failed to parse refactorings", error=str(e))
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=False,
                result={"raw_response": response},
                error=f"Failed to parse refactorings: {str(e)}",
                tokens_used=tokens,
                estimated_cost=cost
            )
    
    def _build_user_prompt(self, input_data: AgentInput) -> str:
        """Build the user prompt with all context"""
        context = input_data.context
        implementation = context.get('implementation', {})
        
        prompt = f"""# Refactoring Task

## Code to Refactor
{self._format_code_to_refactor(context.get('code_to_refactor', {}))}

## Current Issues
{context.get('code_issues', 'No specific issues identified')}

## Implementation Context
{implementation.get('summary', 'No implementation context')}

## Refactoring Goals
{self._format_goals(context.get('refactoring_goals', []))}

## Repository Conventions
{context.get('repo_conventions', 'No conventions detected')}

## Constraints
- Must maintain backward compatibility: {not input_data.policies.get('allow_breaking_changes', False)}
- Performance-critical code: {context.get('is_performance_critical', False)}
- Max LOC per PR: {input_data.policies.get('max_loc_per_pr', 500)}

Analyze and refactor the code following the output format specified."""
        
        return prompt
    
    def _format_code_to_refactor(self, code_dict: Dict[str, str]) -> str:
        """Format code that needs refactoring"""
        if not code_dict:
            return "No code provided"
        
        formatted = []
        for path, content in list(code_dict.items())[:5]:
            formatted.append(f"\n### {path}\n```\n{content[:2000]}\n```")
        
        return "\n".join(formatted)
    
    def _format_goals(self, goals: list) -> str:
        """Format refactoring goals"""
        if not goals:
            return "General code quality improvement"
        
        return "\n".join(f"- {goal}" for goal in goals)
    
    def _parse_refactorings(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured refactorings"""
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
        refactorings = json.loads(response)
        
        # Validate required fields
        required_fields = ["refactorings", "summary"]
        for field in required_fields:
            if field not in refactorings:
                raise ValueError(f"Missing required field: {field}")
        
        return refactorings
    
    def _validate_refactorings(self, refactorings: Dict[str, Any], policies: Dict[str, Any]) -> Dict[str, Any]:
        """Validate refactorings against policies"""
        
        # Check if refactorings are too extensive
        refactoring_list = refactorings.get("refactorings", [])
        if len(refactoring_list) > 10:
            return {
                "valid": False,
                "reason": f"Too many refactorings ({len(refactoring_list)}). Consider breaking into smaller tasks."
            }
        
        # Warn on negative performance impact
        if refactorings.get("performance_impact") == "negative":
            self.logger.warning("Refactoring may have negative performance impact")
        
        return {"valid": True, "reason": ""}
