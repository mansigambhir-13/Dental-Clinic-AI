# RAG implementation
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from utils.helpers import load_text_file, chunk_text
from config import Config

class RAGSystem:
    def __init__(self):
        self.knowledge_base_file = Config.KNOWLEDGE_BASE_FILE
        self.embedding_model_name = Config.EMBEDDING_MODEL
        self.max_chunks = Config.MAX_CHUNKS
        self.chunk_size = Config.CHUNK_SIZE
        
        # Initialize the embedding model
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            self.embedding_model = None
        
        # Load and process knowledge base
        self.knowledge_chunks = []
        self.chunk_embeddings = None
        self.load_knowledge_base()

    def load_knowledge_base(self):
        """Load and process the knowledge base text."""
        knowledge_text = load_text_file(self.knowledge_base_file)
        
        if not knowledge_text:
            print("Warning: Knowledge base file is empty or not found.")
            return

        # Split text into chunks
        self.knowledge_chunks = chunk_text(knowledge_text, self.chunk_size)
        
        if not self.knowledge_chunks:
            print("Warning: No chunks created from knowledge base.")
            return

        # Generate embeddings for chunks
        if self.embedding_model:
            try:
                self.chunk_embeddings = self.embedding_model.encode(self.knowledge_chunks)
                print(f"Successfully loaded {len(self.knowledge_chunks)} knowledge chunks.")
            except Exception as e:
                print(f"Error generating embeddings: {e}")
                self.chunk_embeddings = None
        else:
            print("Warning: Embedding model not available.")

    def search_knowledge(self, query: str, max_results: int = None) -> List[Dict]:
        """
        Search the knowledge base for relevant information.
        Returns list of relevant chunks with similarity scores.
        """
        if not self.knowledge_chunks or not self.embedding_model or self.chunk_embeddings is None:
            return self._fallback_search(query)

        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.chunk_embeddings)[0]
            
            # Get top results
            max_results = max_results or self.max_chunks
            top_indices = np.argsort(similarities)[::-1][:max_results]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    results.append({
                        'content': self.knowledge_chunks[idx],
                        'similarity': float(similarities[idx]),
                        'chunk_id': int(idx)
                    })
            
            return results

        except Exception as e:
            print(f"Error in knowledge search: {e}")
            return self._fallback_search(query)

    def _fallback_search(self, query: str) -> List[Dict]:
        """
        Fallback search using keyword matching when embeddings fail.
        """
        query_lower = query.lower()
        results = []
        
        for i, chunk in enumerate(self.knowledge_chunks):
            chunk_lower = chunk.lower()
            
            # Simple keyword matching
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in chunk_lower)
            
            if matches > 0:
                score = matches / len(query_words)
                results.append({
                    'content': chunk,
                    'similarity': score,
                    'chunk_id': i
                })
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:self.max_chunks]

    def get_context_for_query(self, query: str) -> str:
        """
        Get relevant context from knowledge base for a query.
        Returns concatenated relevant chunks.
        """
        relevant_chunks = self.search_knowledge(query)
        
        if not relevant_chunks:
            return ""
        
        # Combine the most relevant chunks
        context_parts = []
        for chunk_data in relevant_chunks:
            context_parts.append(chunk_data['content'])
        
        return "\n\n".join(context_parts)

    def answer_question_with_context(self, question: str) -> Dict:
        """
        Get context and prepare data for LLM to answer question.
        """
        context = self.get_context_for_query(question)
        relevant_chunks = self.search_knowledge(question)
        
        return {
            'question': question,
            'context': context,
            'relevant_chunks': relevant_chunks,
            'has_context': len(context.strip()) > 0
        }

    def add_to_knowledge_base(self, new_text: str):
        """
        Add new text to the knowledge base and update embeddings.
        """
        try:
            # Add to existing file
            with open(self.knowledge_base_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{new_text}")
            
            # Reload the knowledge base
            self.load_knowledge_base()
            return True
            
        except Exception as e:
            print(f"Error adding to knowledge base: {e}")
            return False

    def get_knowledge_stats(self) -> Dict:
        """Get statistics about the knowledge base."""
        return {
            'total_chunks': len(self.knowledge_chunks),
            'embedding_model': self.embedding_model_name,
            'embeddings_available': self.chunk_embeddings is not None,
            'knowledge_file': self.knowledge_base_file
        }

    def test_rag_system(self) -> Dict:
        """Test the RAG system functionality."""
        test_query = "dental cleaning"
        results = self.search_knowledge(test_query)
        
        return {
            'test_query': test_query,
            'results_found': len(results),
            'system_working': len(results) > 0,
            'sample_result': results[0] if results else None
        }