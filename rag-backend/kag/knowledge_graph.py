"""Knowledge Graph implementation for KAG."""

import networkx as nx
from typing import Dict, List, Tuple, Any
import json


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def add_entity(self, entity_id: str, entity_type: str, properties: Dict[str, Any] = None):
        """Add entity to knowledge graph."""
        self.graph.add_node(
            entity_id,
            type=entity_type,
            properties=properties or {}
        )
    
    def add_relation(self, source: str, target: str, relation_type: str, properties: Dict[str, Any] = None):
        """Add relation between entities."""
        self.graph.add_edge(
            source, 
            target,
            type=relation_type,
            properties=properties or {}
        )
    
    def get_neighbors(self, entity_id: str, relation_type: str = None) -> List[str]:
        """Get neighboring entities."""
        neighbors = []
        for neighbor in self.graph.neighbors(entity_id):
            edge_data = self.graph[entity_id][neighbor]
            if not relation_type or edge_data.get('type') == relation_type:
                neighbors.append(neighbor)
        return neighbors
    
    def get_subgraph(self, entity_id: str, depth: int = 2) -> nx.DiGraph:
        """Extract subgraph around entity."""
        nodes = {entity_id}
        current_level = {entity_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                next_level.update(self.graph.neighbors(node))
            nodes.update(next_level)
            current_level = next_level
            
        return self.graph.subgraph(nodes)
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary."""
        return {
            'nodes': [
                {
                    'id': node,
                    'type': data.get('type'),
                    'properties': data.get('properties', {})
                }
                for node, data in self.graph.nodes(data=True)
            ],
            'edges': [
                {
                    'source': source,
                    'target': target,
                    'type': data.get('type'),
                    'properties': data.get('properties', {})
                }
                for source, target, data in self.graph.edges(data=True)
            ]
        }