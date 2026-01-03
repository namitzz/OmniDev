"""
OmniDev Database Models

SQLAlchemy models for tracking tasks, executions, and agent activities.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Types of agents in the system"""
    PLANNER = "planner"
    FEATURE_DEV = "feature_dev"
    TESTER = "tester"
    REFACTOR = "refactor"
    REVIEWER = "reviewer"


class Task(Base):
    """Main task representing a GitHub issue or work item"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    github_issue_number = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    
    # Git information
    branch_name = Column(String)
    pr_number = Column(Integer, index=True)
    base_commit = Column(String)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Results
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Policies applied
    policies = Column(JSON, default=dict)
    
    # Relationships
    executions = relationship("AgentExecution", back_populates="task", cascade="all, delete-orphan")
    metrics = relationship("TaskMetrics", back_populates="task", uselist=False, cascade="all, delete-orphan")


class AgentExecution(Base):
    """Individual agent execution within a task"""
    __tablename__ = "agent_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, index=True)
    agent_type = Column(SQLEnum(AgentType), nullable=False, index=True)
    
    # Execution details
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.IN_PROGRESS)
    
    # Input/Output
    input_context = Column(JSON)
    output_result = Column(JSON)
    error_message = Column(Text)
    
    # Token usage
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    
    # Model used
    model_name = Column(String)
    
    # Relationships
    task = relationship("Task", back_populates="executions")


class TaskMetrics(Base):
    """Aggregated metrics for a task"""
    __tablename__ = "task_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, unique=True)
    
    # Code metrics
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)
    
    # Test metrics
    tests_added = Column(Integer, default=0)
    tests_passed = Column(Integer, default=0)
    tests_failed = Column(Integer, default=0)
    coverage_before = Column(Float)
    coverage_after = Column(Float)
    
    # Quality metrics
    lint_errors_before = Column(Integer, default=0)
    lint_errors_after = Column(Integer, default=0)
    security_issues_found = Column(Integer, default=0)
    security_issues_fixed = Column(Integer, default=0)
    
    # Cost metrics
    total_tokens_used = Column(Integer, default=0)
    total_estimated_cost = Column(Float, default=0.0)
    
    # Timing
    total_duration_seconds = Column(Float)
    
    # Relationships
    task = relationship("Task", back_populates="metrics")


class RepositoryIndex(Base):
    """Indexed repository information for fast lookup"""
    __tablename__ = "repository_index"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_full_name = Column(String, nullable=False, index=True)
    
    # File information
    file_path = Column(String, nullable=False, index=True)
    file_type = Column(String)
    last_indexed = Column(DateTime, default=datetime.utcnow)
    
    # Content hash for change detection
    content_hash = Column(String, index=True)
    
    # Embeddings reference
    embedding_id = Column(String)
    
    # AST metadata
    ast_metadata = Column(JSON)


class AuditLog(Base):
    """Audit trail for all system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Action details
    action_type = Column(String, nullable=False, index=True)
    actor = Column(String)  # Agent or system component
    
    # Context
    task_id = Column(String, index=True)
    details = Column(JSON)
    
    # Security
    sensitive_data_present = Column(Boolean, default=False)
