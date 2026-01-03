"""
RAG (Retrieval-Augmented Generation) Module

Provides vector search and semantic code understanding using embeddings.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class RAGSystem:
    """
    Vector database and semantic search for codebase understanding.
    
    Uses ChromaDB for vector storage and sentence-transformers for embeddings.
    """
    
    def __init__(self):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        chroma_path = Path(settings.chromadb_path)
        chroma_path.mkdir(parents=True, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="codebase",
            metadata={"description": "Codebase embeddings for semantic search"}
        )
        
        logger.info("RAG system initialized", embedding_model="all-MiniLM-L6-v2")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        embedding = self.embedding_model.encode(text, show_progress_bar=False)
        return embedding.tolist()
    
    def index_file(
        self,
        file_path: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Index a file in the vector database
        
        Returns:
            Document ID
        """
        try:
            # Generate document ID from file path
            doc_id = self._generate_doc_id(file_path)
            
            # Generate embedding
            embedding = self.generate_embedding(content)
            
            # Prepare metadata
            meta = metadata or {}
            meta.update({
                "file_path": file_path,
                "content_length": len(content),
                "content_hash": hashlib.sha256(content.encode()).hexdigest()
            })
            
            # Store in ChromaDB
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content[:1000]],  # Store snippet for retrieval
                metadatas=[meta]
            )
            
            logger.debug("File indexed", file_path=file_path, doc_id=doc_id)
            return doc_id
        
        except Exception as e:
            logger.error("Failed to index file", file_path=file_path, error=str(e))
            raise
    
    def index_code_chunk(
        self,
        file_path: str,
        chunk_content: str,
        chunk_index: int,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Index a code chunk (for large files)
        
        Returns:
            Document ID
        """
        try:
            doc_id = self._generate_doc_id(f"{file_path}:chunk:{chunk_index}")
            
            embedding = self.generate_embedding(chunk_content)
            
            meta = metadata or {}
            meta.update({
                "file_path": file_path,
                "chunk_index": chunk_index,
                "content_length": len(chunk_content),
            })
            
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk_content],
                metadatas=[meta]
            )
            
            return doc_id
        
        except Exception as e:
            logger.error("Failed to index chunk", file_path=file_path, error=str(e))
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant code
        
        Returns:
            List of results with content, metadata, and similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
            
            logger.info("Search completed", query_length=len(query), results_count=len(formatted_results))
            return formatted_results
        
        except Exception as e:
            logger.error("Search failed", query=query[:50], error=str(e))
            raise
    
    def search_by_file_type(
        self,
        query: str,
        file_type: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for code in specific file types"""
        return self.search(
            query=query,
            n_results=n_results,
            filter_metadata={"file_type": file_type}
        )
    
    def get_similar_files(
        self,
        file_path: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Find files similar to a given file"""
        try:
            # Get the file's embedding
            doc_id = self._generate_doc_id(file_path)
            result = self.collection.get(ids=[doc_id])
            
            if not result['documents']:
                logger.warning("File not found in index", file_path=file_path)
                return []
            
            # Use its content for search
            content = result['documents'][0]
            return self.search(query=content, n_results=n_results + 1)[1:]  # Exclude the file itself
        
        except Exception as e:
            logger.error("Failed to find similar files", file_path=file_path, error=str(e))
            return []
    
    def delete_file(self, file_path: str) -> bool:
        """Remove a file from the index"""
        try:
            doc_id = self._generate_doc_id(file_path)
            self.collection.delete(ids=[doc_id])
            logger.info("File removed from index", file_path=file_path)
            return True
        except Exception as e:
            logger.error("Failed to delete file from index", file_path=file_path, error=str(e))
            return False
    
    def clear_index(self) -> bool:
        """Clear all indexed data"""
        try:
            self.chroma_client.delete_collection("codebase")
            self.collection = self.chroma_client.create_collection("codebase")
            logger.info("Index cleared")
            return True
        except Exception as e:
            logger.error("Failed to clear index", error=str(e))
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed codebase"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name,
            }
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {}
    
    def _generate_doc_id(self, file_path: str) -> str:
        """Generate consistent document ID from file path"""
        return hashlib.md5(file_path.encode()).hexdigest()


class CodeChunker:
    """Utility for splitting large code files into chunks"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_lines(self, content: str) -> List[str]:
        """Split content by lines with overlap"""
        lines = content.split('\n')
        chunks = []
        
        i = 0
        while i < len(lines):
            # Get chunk
            chunk_lines = lines[i:i + self.chunk_size]
            chunks.append('\n'.join(chunk_lines))
            
            # Move forward with overlap
            i += self.chunk_size - self.overlap
        
        return chunks
    
    def chunk_by_functions(self, content: str, language: str) -> List[Dict[str, Any]]:
        """
        Split code by functions/classes (requires AST parsing)
        
        This is a simplified version. Full implementation would use tree-sitter.
        """
        # For now, fall back to line-based chunking
        # TODO: Implement AST-based chunking with tree-sitter
        chunks = self.chunk_by_lines(content)
        return [{"content": chunk, "type": "code_block"} for chunk in chunks]
