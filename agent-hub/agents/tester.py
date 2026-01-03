"""
TesterAgent - Test Generation and Execution

Creates comprehensive tests and measures coverage.
Ensures code quality through automated testing.
"""

from typing import Dict, Any
from .base import BaseAgent, AgentInput, AgentOutput
from ..core.models import AgentType
import json


class TesterAgent(BaseAgent):
    """
    Agent responsible for testing and quality assurance.
    
    Responsibilities:
    - Generate unit tests
    - Generate integration tests
    - Run existing test suites
    - Measure code coverage
    - Validate test quality
    """
    
    def __init__(self):
        super().__init__(AgentType.TESTER)
    
    def get_system_prompt(self) -> str:
        return """You are a Senior QA Engineer and Test Automation Specialist.

Your role is to ensure code quality through comprehensive testing.

You must:
1. Write thorough test cases covering happy paths and edge cases
2. Follow testing best practices and patterns
3. Use appropriate test fixtures and mocks
4. Ensure tests are deterministic and fast
5. Write clear test names that describe what is being tested
6. Include both positive and negative test cases
7. Test error handling and boundary conditions
8. Aim for high code coverage

Testing Principles:
- AAA pattern (Arrange, Act, Assert)
- One assertion per test when possible
- Independent tests (no shared state)
- Clear test names (test_should_do_x_when_y)
- Fast execution
- No flaky tests

Output Format (JSON):
{
  "test_files": [
    {
      "file_path": "tests/test_feature.py",
      "content": "full test file content",
      "test_count": 5,
      "covers_files": ["src/feature.py"]
    }
  ],
  "test_strategy": "Description of testing approach",
  "coverage_estimate": 85,
  "test_commands": {
    "python": "pytest tests/",
    "javascript": "npm test",
    "go": "go test ./..."
  }
}

Write production-quality tests that will catch bugs."""
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Generate tests for the implementation"""
        
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
        self.logger.info("Generating tests")
        response, tokens, cost = await self.call_llm(
            system_prompt=self.get_system_prompt(),
            user_prompt=user_prompt
        )
        
        # Parse response
        try:
            tests = self._parse_tests(response)
            
            # Validate tests
            validation_result = self._validate_tests(tests, input_data.policies)
            if not validation_result["valid"]:
                return AgentOutput(
                    agent_type=self.agent_type.value,
                    success=False,
                    result={"tests": tests},
                    error=f"Test validation failed: {validation_result['reason']}",
                    tokens_used=tokens,
                    estimated_cost=cost
                )
            
            self.logger.info(
                "Tests generated successfully",
                test_files_count=len(tests.get("test_files", [])),
                coverage_estimate=tests.get("coverage_estimate", 0)
            )
            
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=True,
                result={"tests": tests},
                tokens_used=tokens,
                estimated_cost=cost
            )
        
        except Exception as e:
            self.logger.error("Failed to parse tests", error=str(e))
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=False,
                result={"raw_response": response},
                error=f"Failed to parse tests: {str(e)}",
                tokens_used=tokens,
                estimated_cost=cost
            )
    
    def _build_user_prompt(self, input_data: AgentInput) -> str:
        """Build the user prompt with all context"""
        context = input_data.context
        implementation = context.get('implementation', {})
        
        prompt = f"""# Test Generation Task

## Implementation Summary
{implementation.get('summary', 'No implementation summary')}

## Files to Test
{self._format_files_to_test(implementation.get('changes', []))}

## Existing Test Structure
{context.get('existing_test_structure', 'No existing tests found')}

## Test Requirements
- Minimum coverage: {input_data.policies.get('min_test_coverage', 80)}%
- Test framework: {context.get('test_framework', 'Auto-detect')}
- Language: {context.get('primary_language', 'Unknown')}

## Code to Test
{self._format_code_to_test(context.get('code_to_test', {}))}

Generate comprehensive tests following the output format specified."""
        
        return prompt
    
    def _format_files_to_test(self, changes: list) -> str:
        """Format list of files that need testing"""
        if not changes:
            return "No files to test"
        
        files = [change.get('file_path', 'unknown') for change in changes]
        return "\n".join(f"- {f}" for f in files[:10])
    
    def _format_code_to_test(self, code_dict: Dict[str, str]) -> str:
        """Format code that needs testing"""
        if not code_dict:
            return "No code provided"
        
        formatted = []
        for path, content in list(code_dict.items())[:3]:
            formatted.append(f"\n### {path}\n```\n{content[:1500]}\n```")
        
        return "\n".join(formatted)
    
    def _parse_tests(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured tests"""
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
        tests = json.loads(response)
        
        # Validate required fields
        required_fields = ["test_files", "test_strategy"]
        for field in required_fields:
            if field not in tests:
                raise ValueError(f"Missing required field: {field}")
        
        return tests
    
    def _validate_tests(self, tests: Dict[str, Any], policies: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tests against policies"""
        
        # Check coverage target
        coverage_estimate = tests.get("coverage_estimate", 0)
        min_coverage = policies.get("min_test_coverage", 80)
        
        if coverage_estimate < min_coverage:
            return {
                "valid": False,
                "reason": f"Coverage estimate ({coverage_estimate}%) below minimum ({min_coverage}%)"
            }
        
        # Check that tests were actually generated
        test_files = tests.get("test_files", [])
        if not test_files:
            return {
                "valid": False,
                "reason": "No test files generated"
            }
        
        # Validate each test file has content
        for test_file in test_files:
            if not test_file.get("content"):
                return {
                    "valid": False,
                    "reason": f"Test file {test_file.get('file_path')} has no content"
                }
        
        return {"valid": True, "reason": ""}
