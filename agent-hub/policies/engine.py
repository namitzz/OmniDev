"""
Policy Engine

Enforces policies and guardrails on agent operations.
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PolicyViolation:
    """Represents a policy violation"""
    policy_name: str
    severity: str  # "warning" or "blocking"
    message: str
    details: Dict[str, Any] = None


class PolicyEngine:
    """
    Enforces policies and guardrails on agent operations.
    
    Policies include:
    - Code size limits
    - Dependency restrictions
    - Breaking change controls
    - Security requirements
    - Retry limits
    """
    
    def __init__(self, custom_policies: Dict[str, Any] = None):
        self.policies = self._load_policies(custom_policies)
        logger.info("Policy engine initialized", policies=list(self.policies.keys()))
    
    def _load_policies(self, custom: Dict[str, Any] = None) -> Dict[str, Any]:
        """Load policies from settings and custom overrides"""
        policies = {
            "max_loc_per_pr": settings.max_loc_per_pr,
            "allow_new_deps": settings.allow_new_deps,
            "min_test_coverage": settings.min_test_coverage,
            "allow_breaking_changes": settings.allow_breaking_changes,
            "max_retry_attempts": settings.max_retry_attempts,
            "enable_static_analysis": settings.enable_static_analysis,
            "enable_security_scan": settings.enable_security_scan,
            "enable_dependency_audit": settings.enable_dependency_audit,
        }
        
        if custom:
            policies.update(custom)
        
        return policies
    
    def check_loc_limit(self, lines_added: int, lines_deleted: int) -> Tuple[bool, PolicyViolation | None]:
        """Check if code changes exceed LOC limit"""
        net_loc = lines_added - lines_deleted
        max_loc = self.policies["max_loc_per_pr"]
        
        if net_loc > max_loc:
            violation = PolicyViolation(
                policy_name="max_loc_per_pr",
                severity="blocking",
                message=f"Net LOC change ({net_loc}) exceeds limit ({max_loc})",
                details={
                    "lines_added": lines_added,
                    "lines_deleted": lines_deleted,
                    "net_change": net_loc,
                    "limit": max_loc
                }
            )
            return False, violation
        
        # Warning if approaching limit
        if net_loc > max_loc * 0.8:
            violation = PolicyViolation(
                policy_name="max_loc_per_pr",
                severity="warning",
                message=f"Net LOC change ({net_loc}) is approaching limit ({max_loc})",
                details={"net_change": net_loc, "limit": max_loc}
            )
            return True, violation
        
        return True, None
    
    def check_new_dependencies(self, new_deps: list) -> Tuple[bool, PolicyViolation | None]:
        """Check if new dependencies are allowed"""
        if not self.policies["allow_new_deps"] and new_deps:
            violation = PolicyViolation(
                policy_name="allow_new_deps",
                severity="blocking",
                message=f"New dependencies are not allowed. Found: {', '.join(new_deps)}",
                details={"new_dependencies": new_deps}
            )
            return False, violation
        
        return True, None
    
    def check_test_coverage(self, coverage: float) -> Tuple[bool, PolicyViolation | None]:
        """Check if test coverage meets minimum requirement"""
        min_coverage = self.policies["min_test_coverage"]
        
        if coverage < min_coverage:
            violation = PolicyViolation(
                policy_name="min_test_coverage",
                severity="blocking",
                message=f"Test coverage ({coverage}%) below minimum ({min_coverage}%)",
                details={
                    "actual_coverage": coverage,
                    "minimum_coverage": min_coverage
                }
            )
            return False, violation
        
        return True, None
    
    def check_breaking_changes(self, has_breaking_changes: bool) -> Tuple[bool, PolicyViolation | None]:
        """Check if breaking changes are allowed"""
        if has_breaking_changes and not self.policies["allow_breaking_changes"]:
            violation = PolicyViolation(
                policy_name="allow_breaking_changes",
                severity="blocking",
                message="Breaking changes are not allowed",
                details={"has_breaking_changes": True}
            )
            return False, violation
        
        return True, None
    
    def check_retry_limit(self, retry_count: int) -> Tuple[bool, PolicyViolation | None]:
        """Check if retry limit has been exceeded"""
        max_retries = self.policies["max_retry_attempts"]
        
        if retry_count >= max_retries:
            violation = PolicyViolation(
                policy_name="max_retry_attempts",
                severity="blocking",
                message=f"Maximum retry attempts ({max_retries}) exceeded",
                details={
                    "retry_count": retry_count,
                    "max_retries": max_retries
                }
            )
            return False, violation
        
        return True, None
    
    def check_security_issues(self, security_issues: list) -> Tuple[bool, PolicyViolation | None]:
        """Check for security vulnerabilities"""
        critical_issues = [issue for issue in security_issues if issue.get("severity") == "critical"]
        
        if critical_issues and self.policies["enable_security_scan"]:
            violation = PolicyViolation(
                policy_name="security_scan",
                severity="blocking",
                message=f"Found {len(critical_issues)} critical security issue(s)",
                details={"critical_issues": critical_issues}
            )
            return False, violation
        
        # Warning for non-critical issues
        if security_issues:
            violation = PolicyViolation(
                policy_name="security_scan",
                severity="warning",
                message=f"Found {len(security_issues)} security issue(s)",
                details={"security_issues": security_issues}
            )
            return True, violation
        
        return True, None
    
    def validate_plan(self, plan: Dict[str, Any]) -> Tuple[bool, list[PolicyViolation]]:
        """Validate an implementation plan against all policies"""
        violations = []
        
        # Check breaking changes
        if plan.get("requires_breaking_changes"):
            passed, violation = self.check_breaking_changes(True)
            if not passed:
                violations.append(violation)
        
        # Check new dependencies
        if plan.get("requires_new_dependencies"):
            # Assume some new deps for now
            passed, violation = self.check_new_dependencies(["example-dep"])
            if not passed:
                violations.append(violation)
        
        # Estimate LOC from complexity
        estimated_loc = self._estimate_loc_from_plan(plan)
        passed, violation = self.check_loc_limit(estimated_loc, 0)
        if violation:
            violations.append(violation)
        
        # Check if any blocking violations
        has_blocking = any(v.severity == "blocking" for v in violations)
        
        return not has_blocking, violations
    
    def validate_implementation(self, implementation: Dict[str, Any]) -> Tuple[bool, list[PolicyViolation]]:
        """Validate an implementation against all policies"""
        violations = []
        
        # Check LOC
        lines_added = implementation.get("estimated_loc_added", 0)
        lines_deleted = implementation.get("estimated_loc_deleted", 0)
        passed, violation = self.check_loc_limit(lines_added, lines_deleted)
        if violation:
            violations.append(violation)
        
        # Check if any blocking violations
        has_blocking = any(v.severity == "blocking" for v in violations)
        
        return not has_blocking, violations
    
    def validate_tests(self, test_results: Dict[str, Any]) -> Tuple[bool, list[PolicyViolation]]:
        """Validate test results against policies"""
        violations = []
        
        # Check coverage
        coverage = test_results.get("coverage", 0)
        passed, violation = self.check_test_coverage(coverage)
        if violation:
            violations.append(violation)
        
        has_blocking = any(v.severity == "blocking" for v in violations)
        
        return not has_blocking, violations
    
    def _estimate_loc_from_plan(self, plan: Dict[str, Any]) -> int:
        """Estimate lines of code from plan complexity"""
        subtasks = plan.get("subtasks", [])
        
        complexity_map = {
            "low": 30,
            "medium": 100,
            "high": 200
        }
        
        total_loc = 0
        for task in subtasks:
            complexity = task.get("estimated_complexity", "medium")
            total_loc += complexity_map.get(complexity, 100)
        
        return total_loc
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of active policies"""
        return {
            "policies": self.policies,
            "enforcement_enabled": True,
        }
