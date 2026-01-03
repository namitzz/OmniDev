"""
Repository Indexer

Scans and indexes repository files for fast search and retrieval.
"""

from pathlib import Path
from typing import List, Dict, Any, Set
import mimetypes
from .vector_store import RAGSystem, CodeChunker
from ..core.logging import get_logger

logger = get_logger(__name__)


class RepositoryIndexer:
    """
    Indexes repository files for search and analysis.
    
    Features:
    - Full-text indexing
    - Vector embeddings for semantic search
    - File type detection
    - Ignore patterns (.gitignore support)
    """
    
    # Code file extensions to index
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java',
        '.c', '.cpp', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
        '.kt', '.scala', '.clj', '.ex', '.exs', '.erl', '.hs',
        '.ml', '.lua', '.r', '.jl', '.dart', '.vue', '.html', '.css',
        '.scss', '.sass', '.less', '.sql', '.sh', '.bash', '.zsh',
        '.fish', '.ps1', '.bat', '.cmd', '.yaml', '.yml', '.json',
        '.toml', '.ini', '.cfg', '.conf', '.xml', '.md', '.rst',
        '.txt', '.dockerfile', '.makefile'
    }
    
    # Directories to ignore
    IGNORE_DIRS = {
        '.git', '.svn', '.hg', 'node_modules', '__pycache__',
        '.pytest_cache', '.mypy_cache', '.tox', 'venv', 'env',
        '.venv', 'dist', 'build', 'target', 'bin', 'obj',
        '.next', '.nuxt', '.cache', 'coverage', '.coverage'
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.rag = RAGSystem()
        self.chunker = CodeChunker(chunk_size=500, overlap=50)
        self.indexed_files: Set[str] = set()
    
    def index_repository(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Index entire repository
        
        Args:
            force_reindex: Re-index all files even if already indexed
        
        Returns:
            Statistics about indexing operation
        """
        logger.info("Starting repository indexing", path=str(self.repo_path))
        
        stats = {
            "total_files": 0,
            "indexed_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
        }
        
        if force_reindex:
            self.rag.clear_index()
            self.indexed_files.clear()
        
        # Walk through repository
        for file_path in self._iter_code_files():
            stats["total_files"] += 1
            
            try:
                # Check if already indexed
                if str(file_path) in self.indexed_files and not force_reindex:
                    stats["skipped_files"] += 1
                    continue
                
                # Index file
                result = self.index_file(file_path)
                if result["success"]:
                    stats["indexed_files"] += 1
                    stats["total_chunks"] += result["chunks"]
                else:
                    stats["failed_files"] += 1
            
            except Exception as e:
                logger.error("Failed to index file", file=str(file_path), error=str(e))
                stats["failed_files"] += 1
        
        logger.info(
            "Repository indexing completed",
            indexed=stats["indexed_files"],
            total=stats["total_files"]
        )
        
        return stats
    
    def index_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Index a single file
        
        Returns:
            Result dictionary with success status and chunk count
        """
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Detect file type
            file_type = self._detect_file_type(file_path)
            
            # Prepare metadata
            metadata = {
                "file_type": file_type,
                "file_name": file_path.name,
                "file_extension": file_path.suffix,
            }
            
            # Index full file for small files
            if len(content) < 2000:
                self.rag.index_file(
                    file_path=str(file_path.relative_to(self.repo_path)),
                    content=content,
                    metadata=metadata
                )
                chunk_count = 1
            else:
                # Chunk large files
                chunks = self.chunker.chunk_by_lines(content)
                chunk_count = 0
                
                for i, chunk in enumerate(chunks):
                    self.rag.index_code_chunk(
                        file_path=str(file_path.relative_to(self.repo_path)),
                        chunk_content=chunk,
                        chunk_index=i,
                        metadata=metadata
                    )
                    chunk_count += 1
            
            # Mark as indexed
            self.indexed_files.add(str(file_path))
            
            return {
                "success": True,
                "chunks": chunk_count,
                "file_size": len(content)
            }
        
        except Exception as e:
            logger.error("File indexing failed", file=str(file_path), error=str(e))
            return {
                "success": False,
                "chunks": 0,
                "error": str(e)
            }
    
    def search_code(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for code matching the query"""
        return self.rag.search(query, n_results=n_results)
    
    def find_similar_code(self, file_path: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find code similar to a given file"""
        return self.rag.get_similar_files(file_path, n_results=n_results)
    
    def get_file_summary(self, file_path: Path) -> Dict[str, Any]:
        """Get summary information about a file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            return {
                "path": str(file_path.relative_to(self.repo_path)),
                "type": self._detect_file_type(file_path),
                "lines": len(lines),
                "size": len(content),
                "extension": file_path.suffix,
            }
        except Exception as e:
            logger.error("Failed to get file summary", file=str(file_path), error=str(e))
            return {}
    
    def _iter_code_files(self):
        """Iterate over all code files in repository"""
        for file_path in self.repo_path.rglob("*"):
            # Skip if not a file
            if not file_path.is_file():
                continue
            
            # Skip ignored directories
            if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                continue
            
            # Skip if not a code file
            if file_path.suffix.lower() not in self.CODE_EXTENSIONS:
                continue
            
            # Skip large binary files
            try:
                if file_path.stat().st_size > 1_000_000:  # 1MB limit
                    continue
            except OSError:
                continue
            
            yield file_path
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect programming language/file type"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript_react',
            '.tsx': 'typescript_react',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c_header',
            '.hpp': 'cpp_header',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.sh': 'shell',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.md': 'markdown',
        }
        
        return extension_map.get(file_path.suffix.lower(), 'text')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        return {
            "indexed_files_count": len(self.indexed_files),
            "vector_db_stats": self.rag.get_stats(),
        }
