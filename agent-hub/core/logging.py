"""
OmniDev Logging Configuration

Provides structured logging with context tracking, run IDs, and observability.
Supports both development (pretty-printed) and production (JSON) formats.
"""

import structlog
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Any
from .config import settings


def setup_logging():
    """Configure structured logging for the application"""
    
    # Ensure log directory exists
    log_path = Path(settings.log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Shared processors for all environments
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    # Development vs Production configuration
    if settings.environment == "development":
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # File handler for persistent logs
    if settings.enable_structured_logging:
        file_handler = logging.FileHandler(settings.log_file_path)
        file_handler.setLevel(logging.INFO)
        logging.root.addHandler(file_handler)


def get_logger(name: str) -> Any:
    """Get a configured logger instance"""
    return structlog.get_logger(name)


class TaskLogger:
    """Logger with automatic task context tracking"""
    
    def __init__(self, task_id: str, agent_name: str):
        self.task_id = task_id
        self.agent_name = agent_name
        self.logger = get_logger(agent_name)
        self.start_time = datetime.now()
    
    def bind(self, **kwargs):
        """Add context to all subsequent log entries"""
        return self.logger.bind(
            task_id=self.task_id,
            agent=self.agent_name,
            **kwargs
        )
    
    def info(self, event: str, **kwargs):
        """Log info level message"""
        self.bind(**kwargs).info(event)
    
    def warning(self, event: str, **kwargs):
        """Log warning level message"""
        self.bind(**kwargs).warning(event)
    
    def error(self, event: str, **kwargs):
        """Log error level message"""
        self.bind(**kwargs).error(event)
    
    def debug(self, event: str, **kwargs):
        """Log debug level message"""
        self.bind(**kwargs).debug(event)
    
    def task_complete(self, success: bool = True, **kwargs):
        """Log task completion with timing"""
        duration = (datetime.now() - self.start_time).total_seconds()
        self.bind(
            duration_seconds=duration,
            success=success,
            **kwargs
        ).info("task_completed")


# Initialize logging on module import
setup_logging()
