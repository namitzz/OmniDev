"""
GitHub Integration Module

Handles all GitHub API interactions including:
- Issue retrieval
- Branch creation
- Pull request management
- Commit operations
- Comments and reviews
"""

from github import Github, GithubException
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest
from typing import Dict, Any, List, Optional
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self):
        self.client = Github(settings.github_token)
        self.repo = self.client.get_repo(f"{settings.github_owner}/{settings.github_repo}")
    
    def get_issue(self, issue_number: int) -> Dict[str, Any]:
        """Get issue details by number"""
        try:
            issue = self.repo.get_issue(issue_number)
            
            return {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body or "",
                "state": issue.state,
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees],
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "author": issue.user.login,
            }
        except GithubException as e:
            logger.error("Failed to get issue", issue_number=issue_number, error=str(e))
            raise
    
    def get_issue_comments(self, issue_number: int) -> List[Dict[str, Any]]:
        """Get all comments on an issue"""
        try:
            issue = self.repo.get_issue(issue_number)
            comments = []
            
            for comment in issue.get_comments():
                comments.append({
                    "id": comment.id,
                    "body": comment.body,
                    "author": comment.user.login,
                    "created_at": comment.created_at.isoformat(),
                })
            
            return comments
        except GithubException as e:
            logger.error("Failed to get issue comments", issue_number=issue_number, error=str(e))
            raise
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> bool:
        """Create a new branch from base branch"""
        try:
            # Get the base branch reference
            base_ref = self.repo.get_git_ref(f"heads/{base_branch}")
            base_sha = base_ref.object.sha
            
            # Create new branch
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha
            )
            
            logger.info("Branch created", branch=branch_name, base=base_branch)
            return True
        except GithubException as e:
            if e.status == 422:
                logger.warning("Branch already exists", branch=branch_name)
                return True  # Branch exists, not a failure
            logger.error("Failed to create branch", branch=branch_name, error=str(e))
            raise
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            logger.info("Pull request created", pr_number=pr.number, head=head_branch)
            
            return {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "state": pr.state,
            }
        except GithubException as e:
            logger.error("Failed to create PR", error=str(e))
            raise
    
    def update_pull_request(self, pr_number: int, title: str = None, body: str = None):
        """Update an existing pull request"""
        try:
            pr = self.repo.get_pull(pr_number)
            
            if title:
                pr.edit(title=title)
            if body:
                pr.edit(body=body)
            
            logger.info("Pull request updated", pr_number=pr_number)
        except GithubException as e:
            logger.error("Failed to update PR", pr_number=pr_number, error=str(e))
            raise
    
    def add_pr_comment(self, pr_number: int, comment: str):
        """Add a comment to a pull request"""
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            
            logger.info("Comment added to PR", pr_number=pr_number)
        except GithubException as e:
            logger.error("Failed to add PR comment", pr_number=pr_number, error=str(e))
            raise
    
    def add_pr_review(
        self,
        pr_number: int,
        event: str,  # APPROVE, REQUEST_CHANGES, COMMENT
        body: str = None,
        comments: List[Dict[str, Any]] = None
    ):
        """Add a review to a pull request"""
        try:
            pr = self.repo.get_pull(pr_number)
            
            if comments:
                # Create review with inline comments
                pr.create_review(
                    body=body,
                    event=event,
                    comments=comments
                )
            else:
                # Simple review without inline comments
                pr.create_review(body=body, event=event)
            
            logger.info("Review added to PR", pr_number=pr_number, event=event)
        except GithubException as e:
            logger.error("Failed to add PR review", pr_number=pr_number, error=str(e))
            raise
    
    def merge_pull_request(
        self,
        pr_number: int,
        merge_method: str = "squash",
        commit_title: str = None,
        commit_message: str = None
    ):
        """Merge a pull request"""
        try:
            pr = self.repo.get_pull(pr_number)
            pr.merge(
                merge_method=merge_method,
                commit_title=commit_title,
                commit_message=commit_message
            )
            
            logger.info("Pull request merged", pr_number=pr_number, method=merge_method)
        except GithubException as e:
            logger.error("Failed to merge PR", pr_number=pr_number, error=str(e))
            raise
    
    def get_file_content(self, file_path: str, ref: str = None) -> str:
        """Get content of a file from the repository"""
        try:
            if ref:
                content = self.repo.get_contents(file_path, ref=ref)
            else:
                content = self.repo.get_contents(file_path)
            
            return content.decoded_content.decode('utf-8')
        except GithubException as e:
            logger.error("Failed to get file content", file=file_path, error=str(e))
            raise
    
    def get_repository_files(self, path: str = "", ref: str = None) -> List[Dict[str, Any]]:
        """List files in a repository directory"""
        try:
            if ref:
                contents = self.repo.get_contents(path, ref=ref)
            else:
                contents = self.repo.get_contents(path)
            
            files = []
            for content in contents:
                files.append({
                    "path": content.path,
                    "name": content.name,
                    "type": content.type,
                    "size": content.size,
                    "sha": content.sha,
                })
            
            return files
        except GithubException as e:
            logger.error("Failed to list repository files", path=path, error=str(e))
            raise
    
    def get_repository_languages(self) -> Dict[str, int]:
        """Get programming languages used in the repository"""
        try:
            return self.repo.get_languages()
        except GithubException as e:
            logger.error("Failed to get repository languages", error=str(e))
            raise
    
    def add_issue_comment(self, issue_number: int, comment: str):
        """Add a comment to an issue"""
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            
            logger.info("Comment added to issue", issue_number=issue_number)
        except GithubException as e:
            logger.error("Failed to add issue comment", issue_number=issue_number, error=str(e))
            raise
    
    def close_issue(self, issue_number: int, comment: str = None):
        """Close an issue with optional comment"""
        try:
            issue = self.repo.get_issue(issue_number)
            
            if comment:
                issue.create_comment(comment)
            
            issue.edit(state="closed")
            
            logger.info("Issue closed", issue_number=issue_number)
        except GithubException as e:
            logger.error("Failed to close issue", issue_number=issue_number, error=str(e))
            raise
