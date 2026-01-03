"""
Test configuration for pytest
"""

import pytest
import os
import sys

# Add agent-hub to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set test environment variables
os.environ["ENVIRONMENT"] = "development"
os.environ["OPENAI_API_KEY"] = "sk-test-key"
os.environ["GITHUB_TOKEN"] = "ghp_test_token"
os.environ["GITHUB_OWNER"] = "test-owner"
os.environ["GITHUB_REPO"] = "test-repo"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["CHROMADB_PATH"] = "./test_chromadb"
os.environ["LOG_LEVEL"] = "ERROR"


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return {
        "test_mode": True,
        "api_url": "http://localhost:8000",
    }


@pytest.fixture(autouse=True)
def cleanup_test_db():
    """Clean up test database after each test"""
    yield
    # Cleanup code here if needed
    import os
    if os.path.exists("test.db"):
        os.remove("test.db")
