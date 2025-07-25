import json
import numpy as np
from typing import List, Tuple

# Optional import for sentence_transformers - fallback to simple text matching if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence_transformers not available. Using simple text matching.")

class RAGSystem:
    def __init__(self, knowledge_base_file: str, embedding_model: str = "all-MiniLM-L6-v2"):
        self.knowledge_base_file = knowledge_base_file
        self.knowledge_chunks = []
        self.embeddings = []
        
        # Only initialize SentenceTransformer if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(embedding_model)
                self.use_embeddings = True
            except Exception as e:
                print(f"Failed to load SentenceTransformer: {e}")
                self.use_embeddings = False
        else:
            self.use_embeddings = False
        
        self._load_knowledge_base()
        if self.use_embeddings:
            self._create_embeddings()
    
    def _load_knowledge_base(self):
        """Load and chunk the knowledge base"""
        try:
            with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple chunking by sentences
            sentences = content.split('. ')
            chunk_size = 200
            
            for i in range(0, len(sentences), 3):  # Group every 3 sentences
                chunk = '. '.join(sentences[i:i+3])
                if len(chunk.strip()) > 20:  # Only add meaningful chunks
                    self.knowledge_chunks.append(chunk.strip())
                    
        except FileNotFoundError:
            print(f"Knowledge base file {self.knowledge_base_file} not found.")
            # Add some default knowledge
            self.knowledge_chunks = [
                "Regular dental checkups are recommended every 6 months.",
                "Good oral hygiene includes brushing twice daily and flossing.",
                "Dental emergencies should be addressed immediately by calling our clinic."
            ]
    
    def _create_embeddings(self):
        """Create embeddings for knowledge chunks"""
        if self.use_embeddings and self.knowledge_chunks:
            try:
                self.embeddings = self.model.encode(self.knowledge_chunks)
            except Exception as e:
                print(f"Failed to create embeddings: {e}")
                self.use_embeddings = False
    
    def _simple_text_search(self, query: str, max_chunks: int = 3) -> List[str]:
        """Simple keyword-based text search as fallback"""
        query_words = set(query.lower().split())
        scored_chunks = []
        
        for chunk in self.knowledge_chunks:
            chunk_words = set(chunk.lower().split())
            # Calculate simple word overlap score
            overlap = len(query_words.intersection(chunk_words))
            if overlap > 0:
                scored_chunks.append((chunk, overlap))
        
        # Sort by score (descending) and return top chunks
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, score in scored_chunks[:max_chunks]]
    
    def _embedding_search(self, query: str, max_chunks: int = 3) -> List[str]:
        """Embedding-based semantic search"""
        if not self.use_embeddings or not self.embeddings:
            return self._simple_text_search(query, max_chunks)
        
        try:
            # Get query embedding
            query_embedding = self.model.encode([query])
            
            # Calculate cosine similarities
            similarities = np.dot(self.embeddings, query_embedding.T).flatten()
            
            # Get top chunks
            top_indices = np.argsort(similarities)[::-1][:max_chunks]
            return [self.knowledge_chunks[i] for i in top_indices]
            
        except Exception as e:
            print(f"Embedding search failed: {e}")
            return self._simple_text_search(query, max_chunks)
    
    def search(self, query: str, max_chunks: int = 3) -> List[str]:
        """Search for relevant knowledge chunks"""
        if self.use_embeddings:
            return self._embedding_search(query, max_chunks)
        else:
            return self._simple_text_search(query, max_chunks)
    
    def get_context(self, query: str, max_chunks: int = 3) -> str:
        """Get context string for the query"""
        relevant_chunks = self.search(query, max_chunks)
        if relevant_chunks:
            return "\n\n".join(relevant_chunks)
        return "No relevant information found in knowledge base."