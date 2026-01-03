"""
Tests for agent implementations
"""

import pytest
from agent-hub.agents import AgentInput, PlannerAgent, FeatureDevAgent, TesterAgent


@pytest.mark.asyncio
async def test_planner_agent_system_prompt():
    """Test that PlannerAgent has a valid system prompt"""
    agent = PlannerAgent()
    prompt = agent.get_system_prompt()
    
    assert prompt is not None
    assert len(prompt) > 100
    assert "plan" in prompt.lower()


@pytest.mark.asyncio
async def test_feature_dev_agent_system_prompt():
    """Test that FeatureDevAgent has a valid system prompt"""
    agent = FeatureDevAgent()
    prompt = agent.get_system_prompt()
    
    assert prompt is not None
    assert len(prompt) > 100
    assert "code" in prompt.lower()


@pytest.mark.asyncio
async def test_agent_abort_logic():
    """Test agent abort logic"""
    agent = PlannerAgent()
    
    # Should not abort with normal context
    context = {"retry_count": 0}
    should_abort, reason = agent.should_abort(context)
    assert should_abort is False
    
    # Should abort with too many retries
    context = {"retry_count": 10}
    should_abort, reason = agent.should_abort(context)
    assert should_abort is True
    assert "retry" in reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
