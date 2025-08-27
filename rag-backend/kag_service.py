"""KAG Service integrating knowledge graph with RAG pipeline."""

from kag import KnowledgeGraph, KAGRetriever, KAGGenerator
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from openai import OpenAI
import os


class KAGService:
    def __init__(self):
        # Initialize components
        self.kg = KnowledgeGraph()
        self.embedding_model = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
        
        # Initialize Chroma with LangChain wrapper
        self.vector_store = None
        self._init_chroma()
        
    def _init_chroma(self):
        """Initialize Chroma with LangChain wrapper."""
        try:
            import chromadb
            print("Starting Chroma initialization...")
            
            # Create directory if it doesn't exist
            import os
            os.makedirs("./chroma_db", exist_ok=True)
            
            # Use persistent directory instead of HTTP client
            self.vector_store = Chroma(
                persist_directory="./chroma_db",
                collection_name="documents",
                embedding_function=self.embedding_model
            )
            print("Chroma initialized successfully with local persistence")
        except ImportError as e:
            print(f"ChromaDB not installed: {e}")
            self.vector_store = None
        except Exception as e:
            print(f"Failed to initialize Chroma: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.vector_store = None
        

        
        # Initialize Ollama client with correct endpoint
        try:
            self.llm_client = OpenAI(
                base_url="http://ollama:11434/v1",
                api_key="ollama"
            )
            print("Ollama client initialized")
        except Exception as e:
            print(f"Ollama not available: {e}")
            self.llm_client = None
        
        # Initialize KAG components after all services are ready
        self._init_kag_components()
        
        # Build initial knowledge graph
        self._build_knowledge_graph()
    
    def _init_kag_components(self):
        """Initialize KAG components after all services are ready."""
        print(f"Initializing KAG components - vector_store: {self.vector_store}, type: {type(self.vector_store)}")
        
        if self.vector_store is not None:
            try:
                print("Attempting to initialize KAG Retriever...")
                self.retriever = KAGRetriever(self.vector_store, self.kg, self.embedding_model)
                print("KAG Retriever initialized successfully")
            except Exception as e:
                print(f"Failed to initialize KAG Retriever: {e}")
                import traceback
                traceback.print_exc()
                self.retriever = None
        else:
            print(f"Vector store not available: {self.vector_store}, skipping retriever initialization")
            self.retriever = None
            
        try:
            self.generator = KAGGenerator(self.llm_client) if self.llm_client else None
            if self.generator:
                print("KAG Generator initialized successfully")
        except Exception as e:
            print(f"Failed to initialize KAG Generator: {e}")
            self.generator = None
        

    
    def query(self, question: str, stream: bool = False):
        """Process query using KAG pipeline."""
        try:
            print(f"Debug: vector_store={self.vector_store}, retriever={self.retriever}")
            if not self.retriever:
                return {"error": "KAG service not properly initialized - Chroma unavailable"}
            
            if not self.generator:
                return {"error": "KAG service not properly initialized - Ollama unavailable"}
                
            # Retrieve relevant documents with KG enhancement
            retrieved_docs = self.retriever.retrieve(question, top_k=5)
            
            # Generate response
            response = self.generator.generate(question, retrieved_docs, stream=stream)
            
            if stream:
                return response  # Return streaming response directly
            else:
                return {
                    "answer": response,
                    "sources": [
                        {
                            "content": doc["content"][:200] + "...",
                            "metadata": doc.get("metadata", {}),
                            "kg_entities": [ctx["entity"] for ctx in doc.get("kg_context", [])]
                        }
                        for doc in retrieved_docs
                    ],
                    "kg_context": self._get_relevant_kg_context(retrieved_docs)
                }
        except Exception as e:
            return {"error": str(e)}
    
    def add_document(self, content: str, metadata: dict = None):
        """Add document to both vector store and knowledge graph."""
        print(f"KAG add_document: Adding document with {len(content)} characters")
        print(f"KAG add_document: Vector store status: {self.vector_store is not None}")
        
        if self.vector_store is None:
            print("Vector store is None, attempting to reinitialize...")
            self._init_chroma()
            self._init_kag_components()
            
        if self.vector_store is None:
            raise Exception("Vector store not available after reinitialization")
            
        try:
            # Add to vector store using LangChain wrapper
            from langchain.schema import Document
            doc = Document(page_content=content, metadata=metadata or {})
            doc_ids = self.vector_store.add_documents([doc])
            print(f"KAG add_document: Added to vector store with IDs: {doc_ids}")
            
            # Persist the changes
            if hasattr(self.vector_store, 'persist'):
                self.vector_store.persist()
                print("KAG add_document: Persisted vector store")
            
            # Extract and add entities/relations to KG
            self._extract_and_add_to_kg(content, doc_ids[0] if doc_ids else "unknown")
            print(f"KAG add_document: Successfully processed document")
        except Exception as e:
            print(f"KAG add_document Error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _build_knowledge_graph(self):
        """Build initial knowledge graph from existing documents."""
        # Sample entities and relations for demonstration
        entities = [
            ("Python", "programming_language", {"description": "High-level programming language"}),
            ("FastAPI", "framework", {"description": "Modern web framework for Python"}),
            ("RAG", "technique", {"description": "Retrieval Augmented Generation"}),
            ("Vector_Database", "technology", {"description": "Database for vector similarity search"}),
        ]
        
        relations = [
            ("FastAPI", "Python", "implemented_in"),
            ("RAG", "Vector_Database", "uses"),
            ("RAG", "Python", "implemented_in"),
        ]
        
        # Add entities
        for entity_id, entity_type, properties in entities:
            self.kg.add_entity(entity_id, entity_type, properties)
        
        # Add relations
        for source, target, relation_type in relations:
            self.kg.add_relation(source, target, relation_type)
    
    def _extract_and_add_to_kg(self, content: str, doc_id: str):
        """Extract entities and relations from content and add to KG."""
        # Simplified entity extraction
        words = content.split()
        entities = [word.strip('.,!?') for word in words if word.istitle() and len(word) > 2]
        
        # Add entities to KG
        for entity in entities:
            if entity not in self.kg.graph.nodes:
                self.kg.add_entity(entity, "extracted_entity", {"source_doc": doc_id})
    
    def _get_relevant_kg_context(self, retrieved_docs: list) -> dict:
        """Get relevant knowledge graph context for visualization."""
        all_entities = set()
        for doc in retrieved_docs:
            for ctx in doc.get("kg_context", []):
                all_entities.add(ctx["entity"])
                all_entities.update([rel["target"] for rel in ctx["relations"]])
        
        # Get subgraph for these entities
        if all_entities:
            subgraph_nodes = set()
            for entity in all_entities:
                if entity in self.kg.graph.nodes:
                    subgraph = self.kg.get_subgraph(entity, depth=1)
                    subgraph_nodes.update(subgraph.nodes())
            
            if subgraph_nodes:
                subgraph = self.kg.graph.subgraph(subgraph_nodes)
                return subgraph.to_dict() if hasattr(subgraph, 'to_dict') else {}
        
        return {}