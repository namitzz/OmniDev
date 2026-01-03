"""
Basic tests for the agent-hub application
"""

import pytest
from agent-hub.core.config import settings


def test_settings_loaded():
    """Test that settings are loaded correctly"""
    assert settings.app_name in ["DevHive", "AutoForge", "MergeMind"]
    assert settings.api_port > 0
    assert settings.environment in ["development", "staging", "production"]


def test_planner_agent_initialization():
    """Test PlannerAgent can be initialized"""
    from agent-hub.agents import PlannerAgent
    
    agent = PlannerAgent()
    assert agent.agent_type.value == "planner"
    assert agent.get_system_prompt() is not None


def test_feature_dev_agent_initialization():
    """Test FeatureDevAgent can be initialized"""
    from agent-hub.agents import FeatureDevAgent
    
    agent = FeatureDevAgent()
    assert agent.agent_type.value == "feature_dev"
    assert agent.get_system_prompt() is not None


def test_policy_engine_initialization():
    """Test PolicyEngine can be initialized"""
    from agent-hub.policies import PolicyEngine
    
    engine = PolicyEngine()
    assert engine.policies is not None
    assert "max_loc_per_pr" in engine.policies


def test_loc_limit_check():
    """Test LOC limit policy check"""
    from agent-hub.policies import PolicyEngine
    
    engine = PolicyEngine()
    
    # Should pass
    passed, violation = engine.check_loc_limit(100, 50)
    assert passed is True
    
    # Should fail
    passed, violation = engine.check_loc_limit(1000, 0)
    assert passed is False
    assert violation is not None


def test_rag_system_initialization():
    """Test RAG system can be initialized"""
    from agent-hub.rag import RAGSystem
    
    # This will create ChromaDB in test environment
    rag = RAGSystem()
    assert rag is not None
    assert rag.embedding_model is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
