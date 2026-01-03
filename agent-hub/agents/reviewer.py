"""
ReviewerAgent - Code Review and Security

Performs comprehensive code review, security analysis, and quality checks.
Acts as the final gatekeeper before changes are merged.
"""

from typing import Dict, Any
from .base import BaseAgent, AgentInput, AgentOutput
from ..core.models import AgentType
import json


class ReviewerAgent(BaseAgent):
    """
    Agent responsible for code review and quality assurance.
    
    Responsibilities:
    - Perform thorough code review
    - Identify security vulnerabilities
    - Check code style and standards
    - Validate test coverage
    - Ensure documentation quality
    - Approve or request changes
    """
    
    def __init__(self):
        super().__init__(AgentType.REVIEWER)
    
    def get_system_prompt(self) -> str:
        return """You are a Principal Engineer conducting code reviews.

Your role is to ensure code quality, security, and maintainability before merge.

You must review for:

1. **Code Quality**
   - Clean, readable code
   - Proper error handling
   - Appropriate abstractions
   - No code duplication
   - Clear naming

2. **Security**
   - No SQL injection vulnerabilities
   - No XSS vulnerabilities
   - Proper input validation
   - Secure authentication/authorization
   - No hardcoded secrets
   - Safe dependency usage

3. **Testing**
   - Adequate test coverage
   - Tests cover edge cases
   - Tests are meaningful
   - No flaky tests

4. **Documentation**
   - Code is self-documenting or commented
   - API changes documented
   - README updated if needed

5. **Architecture**
   - Follows repository patterns
   - Maintains separation of concerns
   - No unnecessary coupling
   - Scalable design

6. **Performance**
   - No obvious performance issues
   - Efficient algorithms
   - Appropriate data structures

Output Format (JSON):
{
  "approved": true|false,
  "summary": "Overall assessment",
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "security|quality|testing|documentation|performance",
      "file": "path/to/file.py",
      "line": 42,
      "description": "What the issue is",
      "recommendation": "How to fix it"
    }
  ],
  "security_score": 95,
  "quality_score": 85,
  "test_coverage_assessment": "adequate|insufficient",
  "requires_changes": true|false
}

Be thorough but fair. Focus on issues that actually matter."""
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Perform code review"""
        
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
        self.logger.info("Performing code review")
        response, tokens, cost = await self.call_llm(
            system_prompt=self.get_system_prompt(),
            user_prompt=user_prompt
        )
        
        # Parse response
        try:
            review = self._parse_review(response)
            
            # Log review results
            self.logger.info(
                "Code review completed",
                approved=review.get("approved", False),
                issues_count=len(review.get("issues", [])),
                security_score=review.get("security_score", 0),
                quality_score=review.get("quality_score", 0)
            )
            
            # Review is always successful, even if code is not approved
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=True,
                result={"review": review},
                tokens_used=tokens,
                estimated_cost=cost
            )
        
        except Exception as e:
            self.logger.error("Failed to parse review", error=str(e))
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=False,
                result={"raw_response": response},
                error=f"Failed to parse review: {str(e)}",
                tokens_used=tokens,
                estimated_cost=cost
            )
    
    def _build_user_prompt(self, input_data: AgentInput) -> str:
        """Build the user prompt with all context"""
        context = input_data.context
        
        prompt = f"""# Code Review Task

## Changes to Review
{self._format_changes(context.get('changes', []))}

## Implementation Summary
{context.get('implementation_summary', 'No summary provided')}

## Test Results
{self._format_test_results(context.get('test_results', {}))}

## Static Analysis Results
{self._format_static_analysis(context.get('static_analysis', {}))}

## Repository Standards
{context.get('repo_conventions', 'No standards defined')}

## Review Criteria
- Min test coverage: {input_data.policies.get('min_test_coverage', 80)}%
- Security scan: {input_data.policies.get('enable_security_scan', True)}
- Breaking changes allowed: {input_data.policies.get('allow_breaking_changes', False)}

Perform a thorough code review following the output format specified."""
        
        return prompt
    
    def _format_changes(self, changes: list) -> str:
        """Format code changes for review"""
        if not changes:
            return "No changes provided"
        
        formatted = []
        for change in changes[:10]:
            if isinstance(change, dict):
                path = change.get('file_path', 'unknown')
                diff = change.get('diff', 'No diff')
                formatted.append(f"\n### {path}\n```diff\n{diff[:1000]}\n```")
        
        return "\n".join(formatted)
    
    def _format_test_results(self, test_results: Dict[str, Any]) -> str:
        """Format test results"""
        if not test_results:
            return "No test results available"
        
        return f"""
- Tests passed: {test_results.get('passed', 0)}
- Tests failed: {test_results.get('failed', 0)}
- Coverage: {test_results.get('coverage', 0)}%
"""
    
    def _format_static_analysis(self, static_analysis: Dict[str, Any]) -> str:
        """Format static analysis results"""
        if not static_analysis:
            return "No static analysis results available"
        
        return f"""
- Lint errors: {static_analysis.get('lint_errors', 0)}
- Security issues: {static_analysis.get('security_issues', 0)}
- Code smells: {static_analysis.get('code_smells', 0)}
"""
    
    def _parse_review(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured review"""
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
        review = json.loads(response)
        
        # Validate required fields
        required_fields = ["approved", "summary", "issues"]
        for field in required_fields:
            if field not in review:
                raise ValueError(f"Missing required field: {field}")
        
        return review
