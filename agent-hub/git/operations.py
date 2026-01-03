"""
Git Operations Module

Handles local git operations including:
- Repository cloning
- Diff generation
- Commit creation
- Branch management
"""

import git
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class GitOperations:
    """Local git operations manager"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or "./workspace"
        self.repo: Optional[git.Repo] = None
    
    def clone_repository(self, repo_url: str, branch: str = "main") -> bool:
        """Clone a repository to the workspace"""
        try:
            Path(self.repo_path).mkdir(parents=True, exist_ok=True)
            
            logger.info("Cloning repository", url=repo_url, branch=branch)
            
            self.repo = git.Repo.clone_from(
                repo_url,
                self.repo_path,
                branch=branch
            )
            
            logger.info("Repository cloned successfully")
            return True
        except git.GitCommandError as e:
            logger.error("Failed to clone repository", error=str(e))
            raise
    
    def open_repository(self, path: str = None) -> bool:
        """Open an existing repository"""
        try:
            repo_path = path or self.repo_path
            self.repo = git.Repo(repo_path)
            logger.info("Repository opened", path=repo_path)
            return True
        except git.InvalidGitRepositoryError as e:
            logger.error("Invalid git repository", path=repo_path, error=str(e))
            raise
    
    def create_branch(self, branch_name: str, base_branch: str = "main") -> bool:
        """Create a new branch locally"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Ensure we're on the base branch
            self.repo.git.checkout(base_branch)
            
            # Create and checkout new branch
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            logger.info("Branch created locally", branch=branch_name)
            return True
        except git.GitCommandError as e:
            logger.error("Failed to create branch", branch=branch_name, error=str(e))
            raise
    
    def commit_changes(self, message: str, files: List[str] = None) -> str:
        """Commit changes to the current branch"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Add files
            if files:
                self.repo.index.add(files)
            else:
                self.repo.git.add(A=True)  # Add all changes
            
            # Commit
            commit = self.repo.index.commit(message)
            
            logger.info("Changes committed", sha=commit.hexsha[:8], message=message)
            return commit.hexsha
        except git.GitCommandError as e:
            logger.error("Failed to commit changes", error=str(e))
            raise
    
    def push_branch(self, branch_name: str, remote: str = "origin") -> bool:
        """Push branch to remote"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            self.repo.git.push(remote, branch_name)
            
            logger.info("Branch pushed", branch=branch_name, remote=remote)
            return True
        except git.GitCommandError as e:
            logger.error("Failed to push branch", branch=branch_name, error=str(e))
            raise
    
    def generate_diff(
        self,
        base: str = "HEAD",
        target: str = None,
        files: List[str] = None
    ) -> str:
        """Generate unified diff"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            if target:
                # Diff between two commits/branches
                diff = self.repo.git.diff(base, target, unified=3)
            elif files:
                # Diff specific files
                diff = self.repo.git.diff(base, '--', *files, unified=3)
            else:
                # Diff all staged changes
                diff = self.repo.git.diff(base, unified=3)
            
            return diff
        except git.GitCommandError as e:
            logger.error("Failed to generate diff", error=str(e))
            raise
    
    def apply_patch(self, patch_content: str) -> bool:
        """Apply a patch/diff to the repository"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Write patch to temporary file
            patch_file = Path(self.repo_path) / ".patch.tmp"
            patch_file.write_text(patch_content)
            
            # Apply patch
            self.repo.git.apply(str(patch_file))
            
            # Clean up
            patch_file.unlink()
            
            logger.info("Patch applied successfully")
            return True
        except git.GitCommandError as e:
            logger.error("Failed to apply patch", error=str(e))
            raise
    
    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Get both staged and unstaged changes
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            
            return list(set(changed_files + staged_files))
        except git.GitCommandError as e:
            logger.error("Failed to get changed files", error=str(e))
            raise
    
    def get_file_content(self, file_path: str, commit: str = "HEAD") -> str:
        """Get content of a file at a specific commit"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            content = self.repo.git.show(f"{commit}:{file_path}")
            return content
        except git.GitCommandError as e:
            logger.error("Failed to get file content", file=file_path, error=str(e))
            raise
    
    def get_commit_info(self, commit_sha: str) -> Dict[str, Any]:
        """Get information about a commit"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            commit = self.repo.commit(commit_sha)
            
            return {
                "sha": commit.hexsha,
                "author": str(commit.author),
                "message": commit.message,
                "date": commit.committed_datetime.isoformat(),
                "files_changed": len(commit.stats.files),
            }
        except git.GitCommandError as e:
            logger.error("Failed to get commit info", sha=commit_sha, error=str(e))
            raise
    
    def run_ripgrep(self, pattern: str, file_patterns: List[str] = None) -> str:
        """Run ripgrep for fast file search"""
        try:
            cmd = ["rg", pattern, "--json"]
            
            if file_patterns:
                for pattern in file_patterns:
                    cmd.extend(["--glob", pattern])
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return result.stdout
        except Exception as e:
            logger.error("Ripgrep search failed", pattern=pattern, error=str(e))
            return ""
    
    def get_repo_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            
            # Count files
            all_files = list(Path(self.repo_path).rglob("*"))
            code_files = [f for f in all_files if f.is_file() and not ".git" in str(f)]
            
            return {
                "total_commits": len(list(self.repo.iter_commits())),
                "branches": len(self.repo.branches),
                "tags": len(self.repo.tags),
                "total_files": len(code_files),
            }
        except Exception as e:
            logger.error("Failed to get repo stats", error=str(e))
            return {}
