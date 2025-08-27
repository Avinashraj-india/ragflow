"""KAG Generator for knowledge-augmented response generation."""

from typing import List, Dict, Any
import json


class KAGGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def generate(self, query: str, retrieved_docs: List[Dict[str, Any]], stream: bool = False):
        """Generate response using retrieved documents and KG context."""
        print(f"Generating response with {len(retrieved_docs)} documents")
        
        if not retrieved_docs:
            return "I don't have any relevant documents to answer your question. Please upload some documents first."
        
        context = self._build_context(retrieved_docs)
        prompt = self._build_prompt(query, context)
        
        try:
            response = self.llm.chat.completions.create(
                model="llama3.2:1b",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that uses both document content and knowledge graph relationships to provide accurate answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=stream
            )
            
            if stream:
                return response
            else:
                return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Build context from retrieved documents and KG."""
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs):
            # Document content
            context_parts.append(f"Document {i+1}:")
            context_parts.append(doc['content'])
            
            # Knowledge graph context
            kg_context = doc.get('kg_context', [])
            if kg_context:
                context_parts.append("Related Knowledge:")
                for entity_info in kg_context:
                    entity = entity_info['entity']
                    relations = entity_info['relations']
                    
                    if relations:
                        context_parts.append(f"- {entity} is related to:")
                        for rel in relations:
                            context_parts.append(f"  * {rel['target']} ({rel['type']})")
            
            context_parts.append("")  # Empty line separator
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build the final prompt for the LLM."""
        return f"""Based on the following context that includes both document content and knowledge graph relationships, please answer the question.

Context:
{context}

Question: {query}

Please provide a comprehensive answer that leverages both the document content and the knowledge relationships shown above."""