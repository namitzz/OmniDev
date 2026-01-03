"""
OmniDev Base Agent

Abstract base class for all agents in the system.
Provides common functionality and enforces agent contract.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import openai
from anthropic import Anthropic
from ..core.config import settings
from ..core.logging import TaskLogger
from ..core.models import AgentExecution, AgentType


@dataclass
class AgentInput:
    """Standard input structure for all agents"""
    task_id: str
    context: Dict[str, Any]
    policies: Dict[str, Any]
    previous_outputs: Dict[str, Any] = None


@dataclass
class AgentOutput:
    """Standard output structure for all agents"""
    agent_type: str
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None
    tokens_used: int = 0
    estimated_cost: float = 0.0


class BaseAgent(ABC):
    """
    Base class for all OmniDev agents.
    
    Each agent must:
    - Have its own prompt
    - Receive only relevant context
    - Produce deterministic outputs
    - Fail safely when unsure
    """
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = None  # Set per task
        
        # Initialize LLM clients
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        else:
            self.anthropic_client = None
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Main processing method - must be implemented by each agent
        
        Args:
            input_data: Standardized input containing task context
        
        Returns:
            AgentOutput with results or error information
        """
        pass
    
    def _get_model_for_agent(self) -> str:
        """Get the configured model for this agent type"""
        model_map = {
            AgentType.PLANNER: settings.planner_model,
            AgentType.FEATURE_DEV: settings.feature_dev_model,
            AgentType.TESTER: settings.tester_model,
            AgentType.REFACTOR: settings.refactor_model,
            AgentType.REVIEWER: settings.reviewer_model,
        }
        return model_map.get(self.agent_type, "gpt-4-turbo-preview")
    
    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> tuple[str, int, float]:
        """
        Call the LLM with the given prompts
        
        Returns:
            Tuple of (response_text, tokens_used, estimated_cost)
        """
        model = self._get_model_for_agent()
        temp = temperature if temperature is not None else settings.code_generation_temperature
        max_tok = max_tokens if max_tokens is not None else settings.max_tokens_per_response
        
        try:
            if model.startswith("gpt"):
                # OpenAI API
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temp,
                    max_tokens=max_tok
                )
                
                content = response.choices[0].message.content
                tokens = response.usage.total_tokens
                
                # Estimate cost (approximate rates)
                cost = self._estimate_openai_cost(model, response.usage.prompt_tokens, response.usage.completion_tokens)
                
                return content, tokens, cost
            
            elif model.startswith("claude") and self.anthropic_client:
                # Anthropic API
                response = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=max_tok,
                    temperature=temp,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                content = response.content[0].text
                tokens = response.usage.input_tokens + response.usage.output_tokens
                
                # Estimate cost
                cost = self._estimate_anthropic_cost(model, response.usage.input_tokens, response.usage.output_tokens)
                
                return content, tokens, cost
            
            else:
                raise ValueError(f"Unsupported model: {model}")
        
        except Exception as e:
            self.logger.error(f"LLM call failed", error=str(e))
            raise
    
    def _estimate_openai_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate OpenAI API cost based on token usage"""
        # Approximate pricing (per 1K tokens) as of 2024
        rates = {
            "gpt-4-turbo-preview": (0.01, 0.03),
            "gpt-4": (0.03, 0.06),
            "gpt-3.5-turbo": (0.0005, 0.0015),
        }
        
        # Default to GPT-4 pricing
        prompt_rate, completion_rate = rates.get(model, (0.01, 0.03))
        
        cost = (prompt_tokens / 1000 * prompt_rate) + (completion_tokens / 1000 * completion_rate)
        return round(cost, 6)
    
    def _estimate_anthropic_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate Anthropic API cost based on token usage"""
        # Approximate pricing (per 1K tokens) as of 2024
        rates = {
            "claude-3-opus": (0.015, 0.075),
            "claude-3-sonnet": (0.003, 0.015),
        }
        
        # Default to Opus pricing
        input_rate, output_rate = rates.get(model, (0.015, 0.075))
        
        cost = (input_tokens / 1000 * input_rate) + (output_tokens / 1000 * output_rate)
        return round(cost, 6)
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute the agent with error handling and logging
        
        This is the public interface - it wraps process() with common functionality
        """
        self.logger = TaskLogger(input_data.task_id, self.agent_type.value)
        
        self.logger.info(
            "agent_execution_started",
            agent_type=self.agent_type.value
        )
        
        try:
            output = await self.process(input_data)
            
            self.logger.info(
                "agent_execution_completed",
                success=output.success,
                tokens_used=output.tokens_used,
                estimated_cost=output.estimated_cost
            )
            
            return output
        
        except Exception as e:
            self.logger.error(
                "agent_execution_failed",
                error=str(e),
                agent_type=self.agent_type.value
            )
            
            return AgentOutput(
                agent_type=self.agent_type.value,
                success=False,
                result={},
                error=str(e)
            )
    
    def should_abort(self, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Determine if execution should abort based on policies and context
        
        Returns:
            Tuple of (should_abort, reason)
        """
        # Check if previous agents failed critically
        if context.get("critical_failure"):
            return True, "Previous critical failure detected"
        
        # Check retry count
        retry_count = context.get("retry_count", 0)
        if retry_count >= settings.max_retry_attempts:
            return True, f"Maximum retry attempts ({settings.max_retry_attempts}) exceeded"
        
        return False, ""
