"""KAG Retriever combining vector search with knowledge graph."""

from typing import List, Dict, Any
import numpy as np
from .knowledge_graph import KnowledgeGraph


class KAGRetriever:
    def __init__(self, vector_store, knowledge_graph: KnowledgeGraph, embedding_model):
        self.vector_store = vector_store
        self.kg = knowledge_graph
        self.embedding_model = embedding_model
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve using both vector similarity and knowledge graph."""
        # Vector-based retrieval
        vector_results = self._vector_retrieve(query, top_k * 2)
        
        # Knowledge graph expansion
        kg_enhanced_results = []
        for result in vector_results:
            enhanced_result = self._enhance_with_kg(result)
            kg_enhanced_results.append(enhanced_result)
        
        # Re-rank and return top_k
        return self._rerank(kg_enhanced_results, query)[:top_k]
    
    def _vector_retrieve(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Perform vector-based retrieval."""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            print(f"Vector search found {len(results)} documents for query: '{query}'")
            
            formatted_results = [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': score,
                    'entities': self._extract_entities(doc.page_content)
                }
                for doc, score in results
            ]
            
            if not formatted_results:
                print("No documents found in vector store")
            
            return formatted_results
        except Exception as e:
            print(f"Error in vector retrieval: {e}")
            return []
    
    def _enhance_with_kg(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance result with knowledge graph context."""
        entities = result.get('entities', [])
        kg_context = []
        
        for entity in entities:
            if entity in self.kg.graph.nodes:
                # Get entity neighbors and relations
                neighbors = self.kg.get_neighbors(entity)
                subgraph = self.kg.get_subgraph(entity, depth=1)
                
                kg_context.append({
                    'entity': entity,
                    'neighbors': neighbors,
                    'relations': [
                        {
                            'target': target,
                            'type': data.get('type'),
                            'properties': data.get('properties', {})
                        }
                        for _, target, data in subgraph.edges(entity, data=True)
                    ]
                })
        
        result['kg_context'] = kg_context
        return result
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (simplified)."""
        # This is a placeholder - in practice, use NER models
        words = text.split()
        entities = [word for word in words if word.istitle() and len(word) > 2]
        return entities
    
    def _rerank(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Re-rank results considering KG context."""
        # Simple scoring: combine vector score with KG relevance
        for result in results:
            kg_score = len(result.get('kg_context', [])) * 0.1
            result['final_score'] = result['score'] + kg_score
        
        return sorted(results, key=lambda x: x['final_score'], reverse=True)