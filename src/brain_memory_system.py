#!/usr/bin/env python3
"""
Brain-like Memory System Enhancement for MCP Context Manager
Implements multilayered memory architecture with neural-style interconnections.
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
from collections import defaultdict
import math


class MemoryLayer(str, Enum):
    """Different layers of memory following human brain architecture."""
    SHORT_TERM = "short_term"      # Working memory, temporary storage
    LONG_TERM = "long_term"        # Persistent knowledge and facts
    EPISODIC = "episodic"          # Specific events and experiences
    PROCEDURAL = "procedural"      # Skills and learned patterns
    SEMANTIC = "semantic"          # Conceptual knowledge and relationships


class ConnectionType(str, Enum):
    """Types of connections between memory nodes."""
    SEMANTIC = "semantic"          # Conceptual similarity
    TEMPORAL = "temporal"          # Time-based sequence
    CAUSAL = "causal"             # Cause-effect relationship
    CONTEXTUAL = "contextual"     # Same context/project
    FUNCTIONAL = "functional"     # Similar function/tool/technique
    ANALOGICAL = "analogical"     # Similar patterns or solutions


class MemoryState(str, Enum):
    """Lifecycle states of memories."""
    FRESH = "fresh"               # Recently created
    ACTIVE = "active"             # Frequently accessed
    STABLE = "stable"             # Established knowledge
    DORMANT = "dormant"           # Infrequently accessed
    CONSOLIDATED = "consolidated"  # Integrated into broader knowledge


@dataclass
class MemoryMetadata:
    """Extended metadata for brain-like memory management."""
    # Core metadata
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    # Brain-like attributes
    emotional_weight: float = 0.0    # Importance/priority weight
    integration_depth: float = 0.0   # How embedded in broader knowledge
    decay_rate: float = 0.1          # How quickly memory fades
    reinforcement_count: int = 0     # How often referenced/used
    
    # Memory layer information
    memory_layer: MemoryLayer = MemoryLayer.SHORT_TERM
    memory_state: MemoryState = MemoryState.FRESH
    
    # Classification metadata
    topic_categories: List[str] = field(default_factory=list)
    skill_categories: List[str] = field(default_factory=list)
    context_categories: List[str] = field(default_factory=list)
    
    # Connection metadata
    connection_strength_total: float = 0.0
    connected_memory_count: int = 0


@dataclass
class MemoryConnection:
    """Represents a connection between two memories."""
    source_memory_id: str
    target_memory_id: str
    connection_type: ConnectionType
    strength: float = 0.5  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_reinforced: datetime = field(default_factory=datetime.now)
    reinforcement_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryNode:
    """Enhanced memory node with brain-like attributes."""
    id: str
    content: str
    memory_type: str  # Original memory type from existing system
    project_id: str
    tags: List[str]
    embedding: Optional[List[float]] = None
    
    # Brain enhancements
    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)
    connections: Dict[str, MemoryConnection] = field(default_factory=dict)
    
    # Classification hierarchies
    topic_path: List[str] = field(default_factory=list)  # e.g., ["Programming", "Frontend", "React"]
    skill_path: List[str] = field(default_factory=list)  # e.g., ["Development", "Debugging", "React"]


class BrainMemorySystem:
    """
    Brain-like memory system that extends the existing MCP memory functionality.
    Implements multilayered memory with neural-style interconnections.
    """
    
    def __init__(self, db_path: str, embedding_service=None):
        self.db_path = db_path
        self.embedding_service = embedding_service
        self.logger = logging.getLogger(__name__)
        
        # Memory storage
        self.memory_nodes: Dict[str, MemoryNode] = {}
        self.connections: Dict[str, Dict[str, MemoryConnection]] = defaultdict(dict)
        
        # Classification hierarchies
        self.topic_hierarchy = self._init_topic_hierarchy()
        self.skill_hierarchy = self._init_skill_hierarchy()
        
        # Configuration
        self.config = {
            "short_term_limit": 50,          # Max memories in short-term
            "memory_decay_threshold": 0.1,   # Below this, memory becomes dormant
            "connection_strength_threshold": 0.3,  # Minimum strength for connections
            "consolidation_threshold": 10,    # Access count for consolidation
            "similarity_threshold": 0.7,     # For automatic connection creation
            "memory_promotion_threshold": 5,  # Access count for layer promotion
        }
        
        self._init_brain_database()
        self._load_memories()
    
    def _init_topic_hierarchy(self) -> Dict[str, List[str]]:
        """Initialize hierarchical topic classification."""
        return {
            "Programming": [
                "Frontend", "Backend", "DevOps", "Mobile", "Desktop",
                "Languages", "Frameworks", "Libraries", "Tools"
            ],
            "Frontend": [
                "React", "Vue", "Angular", "HTML", "CSS", "JavaScript", "TypeScript"
            ],
            "Backend": [
                "Python", "Node.js", "Java", "Go", "Rust", "APIs", "Databases"
            ],
            "DevOps": [
                "Docker", "Kubernetes", "CI/CD", "Monitoring", "Cloud", "Infrastructure"
            ],
            "Problem Solving": [
                "Debugging", "Optimization", "Architecture", "Design Patterns", "Algorithms"
            ],
            "Project Management": [
                "Planning", "Task Management", "Documentation", "Testing", "Deployment"
            ]
        }
    
    def _init_skill_hierarchy(self) -> Dict[str, List[str]]:
        """Initialize hierarchical skill classification."""
        return {
            "Development": [
                "Coding", "Debugging", "Testing", "Refactoring", "Code Review"
            ],
            "Design": [
                "Architecture", "UI/UX", "System Design", "Database Design"
            ],
            "Analysis": [
                "Problem Analysis", "Performance Analysis", "Code Analysis"
            ],
            "Communication": [
                "Documentation", "Explanation", "Teaching", "Collaboration"
            ]
        }
    
    def _init_brain_database(self):
        """Initialize database tables for brain-like memory system."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Memory nodes table (extends existing memories)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brain_memory_nodes (
                id TEXT PRIMARY KEY,
                original_memory_id INTEGER,
                memory_layer TEXT NOT NULL,
                memory_state TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                emotional_weight REAL DEFAULT 0.0,
                integration_depth REAL DEFAULT 0.0,
                decay_rate REAL DEFAULT 0.1,
                reinforcement_count INTEGER DEFAULT 0,
                topic_categories TEXT,  -- JSON array
                skill_categories TEXT,  -- JSON array
                context_categories TEXT,  -- JSON array
                topic_path TEXT,  -- JSON array
                skill_path TEXT,  -- JSON array
                connection_strength_total REAL DEFAULT 0.0,
                connected_memory_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Memory connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brain_memory_connections (
                id TEXT PRIMARY KEY,
                source_memory_id TEXT NOT NULL,
                target_memory_id TEXT NOT NULL,
                connection_type TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_reinforced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reinforcement_count INTEGER DEFAULT 0,
                metadata TEXT,  -- JSON
                FOREIGN KEY (source_memory_id) REFERENCES brain_memory_nodes (id),
                FOREIGN KEY (target_memory_id) REFERENCES brain_memory_nodes (id)
            )
        ''')
        
        # Classification paths table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brain_classification_paths (
                memory_id TEXT NOT NULL,
                path_type TEXT NOT NULL,  -- 'topic' or 'skill'
                path_json TEXT NOT NULL,  -- JSON array of path
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES brain_memory_nodes (id)
            )
        ''')
        
        # Memory access log for pattern analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brain_memory_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL,
                access_type TEXT NOT NULL,  -- 'read', 'write', 'connection'
                context TEXT,  -- What triggered the access
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES brain_memory_nodes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def enhance_existing_memory(self, memory_id: str, memory_data: Dict[str, Any]) -> MemoryNode:
        """
        Enhance an existing memory with brain-like attributes.
        This integrates with the existing memory system.
        """
        node = MemoryNode(
            id=memory_id,
            content=memory_data.get("content", ""),
            memory_type=memory_data.get("memory_type", "fact"),
            project_id=memory_data.get("project_id", "default"),
            tags=memory_data.get("tags", []),
            embedding=memory_data.get("embedding")
        )
        
        # Classify and enhance
        await self._classify_memory(node)
        await self._determine_memory_layer(node)
        await self._calculate_emotional_weight(node)
        
        # Store enhanced memory
        self.memory_nodes[memory_id] = node
        await self._save_memory_node(node)
        
        # Find and create connections
        await self._auto_create_connections(node)
        
        return node
    
    async def _classify_memory(self, node: MemoryNode):
        """Classify memory into hierarchical categories."""
        content_lower = node.content.lower()
        tags_lower = [tag.lower() for tag in node.tags]
        
        # Topic classification
        topic_categories = []
        topic_path = []
        
        for main_topic, subtopics in self.topic_hierarchy.items():
            main_topic_lower = main_topic.lower()
            
            # Check if main topic is mentioned
            if main_topic_lower in content_lower or any(main_topic_lower in tag for tag in tags_lower):
                topic_categories.append(main_topic)
                topic_path.append(main_topic)
                
                # Check subtopics
                for subtopic in subtopics:
                    subtopic_lower = subtopic.lower()
                    if subtopic_lower in content_lower or any(subtopic_lower in tag for tag in tags_lower):
                        topic_categories.append(subtopic)
                        if len(topic_path) == 1:  # Only add if we haven't found a deeper path
                            topic_path.append(subtopic)
        
        # Skill classification
        skill_categories = []
        skill_path = []
        
        for main_skill, subskills in self.skill_hierarchy.items():
            main_skill_lower = main_skill.lower()
            
            # Check if main skill is mentioned
            if main_skill_lower in content_lower or any(main_skill_lower in tag for tag in tags_lower):
                skill_categories.append(main_skill)
                skill_path.append(main_skill)
                
                # Check subskills
                for subskill in subskills:
                    subskill_lower = subskill.lower()
                    if subskill_lower in content_lower or any(subskill_lower in tag for tag in tags_lower):
                        skill_categories.append(subskill)
                        if len(skill_path) == 1:
                            skill_path.append(subskill)
        
        # Update metadata
        node.metadata.topic_categories = topic_categories
        node.metadata.skill_categories = skill_categories
        node.topic_path = topic_path
        node.skill_path = skill_path
        
        # Context categories (from project and tags)
        node.metadata.context_categories = [node.project_id] + node.tags
    
    async def _determine_memory_layer(self, node: MemoryNode):
        """Determine the appropriate memory layer for the node."""
        content = node.content.lower()
        memory_type = node.memory_type.lower()
        
        # Heuristics for layer assignment
        if memory_type == "task" and "todo" in content:
            node.metadata.memory_layer = MemoryLayer.SHORT_TERM
        elif "procedure" in content or "how to" in content or "step" in content:
            node.metadata.memory_layer = MemoryLayer.PROCEDURAL
        elif any(word in content for word in ["remember", "happened", "did", "was", "were"]):
            node.metadata.memory_layer = MemoryLayer.EPISODIC
        elif memory_type in ["fact", "preference"] or "is" in content or "define" in content:
            node.metadata.memory_layer = MemoryLayer.SEMANTIC
        else:
            node.metadata.memory_layer = MemoryLayer.LONG_TERM
    
    async def _calculate_emotional_weight(self, node: MemoryNode):
        """Calculate emotional/priority weight based on content analysis."""
        content = node.content.lower()
        weight = 0.5  # Base weight
        
        # Priority indicators
        priority_words = {
            "critical": 0.4, "urgent": 0.4, "important": 0.3,
            "must": 0.3, "need": 0.2, "should": 0.1,
            "error": 0.3, "bug": 0.3, "fix": 0.2,
            "deadline": 0.3, "asap": 0.4
        }
        
        for word, boost in priority_words.items():
            if word in content:
                weight += boost
        
        # Length and complexity indicators
        if len(node.content) > 200:
            weight += 0.1
        if len(node.tags) > 3:
            weight += 0.1
        
        # Clamp to valid range
        node.metadata.emotional_weight = max(0.0, min(1.0, weight))
    
    async def _auto_create_connections(self, node: MemoryNode):
        """Automatically create connections to related memories."""
        if not node.embedding or not self.embedding_service:
            return
        
        # Find similar memories
        similar_memories = await self._find_similar_memories(node)
        
        for similar_id, similarity_score in similar_memories:
            if similarity_score > self.config["similarity_threshold"]:
                await self._create_connection(
                    node.id, similar_id, 
                    ConnectionType.SEMANTIC, 
                    similarity_score
                )
        
        # Create contextual connections (same project)
        contextual_memories = await self._find_contextual_memories(node)
        for contextual_id in contextual_memories:
            await self._create_connection(
                node.id, contextual_id,
                ConnectionType.CONTEXTUAL,
                0.6
            )
        
        # Create temporal connections (recent memories)
        recent_memories = await self._find_recent_memories(node, hours=24)
        for recent_id in recent_memories:
            await self._create_connection(
                node.id, recent_id,
                ConnectionType.TEMPORAL,
                0.4
            )
    
    async def _find_similar_memories(self, node: MemoryNode) -> List[Tuple[str, float]]:
        """Find memories with similar embeddings."""
        if not node.embedding:
            return []
        
        similar = []
        for memory_id, memory_node in self.memory_nodes.items():
            if memory_id == node.id or not memory_node.embedding:
                continue
            
            similarity = self.embedding_service.calculate_similarity(
                node.embedding, memory_node.embedding
            )
            if similarity > self.config["connection_strength_threshold"]:
                similar.append((memory_id, similarity))
        
        return sorted(similar, key=lambda x: x[1], reverse=True)[:10]
    
    async def _find_contextual_memories(self, node: MemoryNode) -> List[str]:
        """Find memories in the same context (project, tags)."""
        contextual = []
        for memory_id, memory_node in self.memory_nodes.items():
            if memory_id == node.id:
                continue
            
            # Same project
            if memory_node.project_id == node.project_id:
                contextual.append(memory_id)
            
            # Shared tags
            elif set(memory_node.tags) & set(node.tags):
                contextual.append(memory_id)
        
        return contextual[:10]
    
    async def _find_recent_memories(self, node: MemoryNode, hours: int = 24) -> List[str]:
        """Find memories created recently."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []
        
        for memory_id, memory_node in self.memory_nodes.items():
            if (memory_id != node.id and 
                memory_node.metadata.created_at > cutoff):
                recent.append(memory_id)
        
        return recent[:5]
    
    async def _create_connection(self, source_id: str, target_id: str, 
                               connection_type: ConnectionType, strength: float):
        """Create a connection between two memories."""
        connection_id = f"{source_id}->{target_id}"
        
        connection = MemoryConnection(
            source_memory_id=source_id,
            target_memory_id=target_id,
            connection_type=connection_type,
            strength=strength
        )
        
        # Store in memory
        self.connections[source_id][target_id] = connection
        
        # Update node metadata
        if source_id in self.memory_nodes:
            self.memory_nodes[source_id].connections[target_id] = connection
            self.memory_nodes[source_id].metadata.connected_memory_count += 1
            self.memory_nodes[source_id].metadata.connection_strength_total += strength
        
        # Save to database
        await self._save_connection(connection)
    
    async def search_memories_with_context(self, query: str, project_id: str = None, 
                                         focus_areas: List[str] = None) -> List[Dict[str, Any]]:
        """
        Enhanced memory search that finds similar experiences and connects related knowledge.
        """
        # Generate embedding for query
        query_embedding = None
        if self.embedding_service:
            query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Find direct matches
        direct_matches = await self._search_direct_matches(query, project_id, focus_areas)
        
        # Find similar experiences (analogical reasoning)
        similar_experiences = await self._search_similar_experiences(
            query_embedding, focus_areas
        )
        
        # Find connected knowledge through graph traversal
        connected_knowledge = await self._search_connected_knowledge(
            direct_matches, max_depth=2
        )
        
        # Combine and rank results
        all_results = self._combine_and_rank_results(
            direct_matches, similar_experiences, connected_knowledge
        )
        
        return all_results[:20]  # Return top 20 results
    
    async def _search_direct_matches(self, query: str, project_id: str = None,
                                   focus_areas: List[str] = None) -> List[Dict[str, Any]]:
        """Search for direct content matches."""
        matches = []
        query_lower = query.lower()
        
        for memory_id, node in self.memory_nodes.items():
            # Content match
            content_score = 0.0
            if query_lower in node.content.lower():
                content_score = 0.8
            
            # Tag match
            tag_score = 0.0
            for tag in node.tags:
                if query_lower in tag.lower():
                    tag_score = max(tag_score, 0.6)
            
            # Focus area match
            focus_score = 0.0
            if focus_areas:
                for area in focus_areas:
                    if (area.lower() in node.metadata.topic_categories or
                        area.lower() in node.metadata.skill_categories):
                        focus_score = 0.4
            
            # Project filter
            if project_id and node.project_id != project_id:
                continue
            
            total_score = max(content_score, tag_score, focus_score)
            if total_score > 0:
                matches.append({
                    "memory_id": memory_id,
                    "node": node,
                    "score": total_score,
                    "match_type": "direct"
                })
        
        return sorted(matches, key=lambda x: x["score"], reverse=True)
    
    async def _search_similar_experiences(self, query_embedding: List[float],
                                        focus_areas: List[str] = None) -> List[Dict[str, Any]]:
        """Search for similar experiences using embeddings."""
        if not query_embedding:
            return []
        
        similar = []
        for memory_id, node in self.memory_nodes.items():
            if not node.embedding:
                continue
            
            similarity = self.embedding_service.calculate_similarity(
                query_embedding, node.embedding
            )
            
            if similarity > 0.5:  # Threshold for similarity
                # Boost score for episodic memories (experiences)
                score = similarity
                if node.metadata.memory_layer == MemoryLayer.EPISODIC:
                    score *= 1.2
                
                similar.append({
                    "memory_id": memory_id,
                    "node": node,
                    "score": score,
                    "match_type": "similar_experience"
                })
        
        return sorted(similar, key=lambda x: x["score"], reverse=True)
    
    async def _search_connected_knowledge(self, seed_memories: List[Dict[str, Any]], 
                                        max_depth: int = 2) -> List[Dict[str, Any]]:
        """Search connected knowledge through graph traversal."""
        visited = set()
        queue = [(m["memory_id"], 0) for m in seed_memories]  # (id, depth)
        connected = []
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if current_id in visited or depth >= max_depth:
                continue
            
            visited.add(current_id)
            
            # Get connections for current memory
            if current_id in self.connections:
                for target_id, connection in self.connections[current_id].items():
                    if target_id not in visited and connection.strength > 0.4:
                        # Add connected memory
                        if target_id in self.memory_nodes:
                            connected.append({
                                "memory_id": target_id,
                                "node": self.memory_nodes[target_id],
                                "score": connection.strength * (0.8 ** depth),  # Decay by depth
                                "match_type": f"connected_{connection.connection_type.value}"
                            })
                        
                        # Add to queue for further traversal
                        queue.append((target_id, depth + 1))
        
        return connected
    
    def _combine_and_rank_results(self, *result_lists) -> List[Dict[str, Any]]:
        """Combine multiple result lists and rank by relevance."""
        combined = {}
        
        for result_list in result_lists:
            for result in result_list:
                memory_id = result["memory_id"]
                if memory_id in combined:
                    # Boost score for multiple match types
                    combined[memory_id]["score"] = max(
                        combined[memory_id]["score"], 
                        result["score"]
                    ) + (result["score"] * 0.2)
                else:
                    combined[memory_id] = result
        
        # Apply memory layer and state boosts
        for result in combined.values():
            node = result["node"]
            
            # Boost for active memories
            if node.metadata.memory_state == MemoryState.ACTIVE:
                result["score"] *= 1.1
            
            # Boost for high emotional weight
            result["score"] *= (1 + node.metadata.emotional_weight * 0.3)
            
            # Boost for high integration depth
            result["score"] *= (1 + node.metadata.integration_depth * 0.2)
        
        return sorted(combined.values(), key=lambda x: x["score"], reverse=True)
    
    async def promote_memory_layers(self):
        """Promote memories between layers based on usage patterns."""
        current_time = datetime.now()
        
        for memory_id, node in self.memory_nodes.items():
            metadata = node.metadata
            
            # Calculate time-based decay
            time_since_access = (current_time - metadata.last_accessed).total_seconds() / 3600  # hours
            decay_factor = math.exp(-metadata.decay_rate * time_since_access)
            
            # Update memory state based on usage
            if metadata.access_count >= self.config["consolidation_threshold"]:
                if metadata.memory_state != MemoryState.CONSOLIDATED:
                    metadata.memory_state = MemoryState.CONSOLIDATED
                    metadata.integration_depth = min(1.0, metadata.integration_depth + 0.2)
            elif metadata.access_count >= 5:
                metadata.memory_state = MemoryState.ACTIVE
            elif decay_factor < self.config["memory_decay_threshold"]:
                metadata.memory_state = MemoryState.DORMANT
            
            # Promote between layers
            if (metadata.memory_layer == MemoryLayer.SHORT_TERM and 
                metadata.access_count >= self.config["memory_promotion_threshold"]):
                
                # Determine target layer based on content
                if node.metadata.memory_layer == MemoryLayer.SHORT_TERM:
                    if "procedure" in node.content.lower():
                        metadata.memory_layer = MemoryLayer.PROCEDURAL
                    elif any(word in node.content.lower() for word in ["happened", "did", "was"]):
                        metadata.memory_layer = MemoryLayer.EPISODIC
                    else:
                        metadata.memory_layer = MemoryLayer.LONG_TERM
            
            # Save changes
            await self._save_memory_node(node)
    
    async def _save_memory_node(self, node: MemoryNode):
        """Save memory node to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO brain_memory_nodes (
                id, memory_layer, memory_state, access_count, last_accessed,
                emotional_weight, integration_depth, decay_rate, reinforcement_count,
                topic_categories, skill_categories, context_categories,
                topic_path, skill_path, connection_strength_total, connected_memory_count,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            node.id, node.metadata.memory_layer.value, node.metadata.memory_state.value,
            node.metadata.access_count, node.metadata.last_accessed,
            node.metadata.emotional_weight, node.metadata.integration_depth,
            node.metadata.decay_rate, node.metadata.reinforcement_count,
            json.dumps(node.metadata.topic_categories),
            json.dumps(node.metadata.skill_categories),
            json.dumps(node.metadata.context_categories),
            json.dumps(node.topic_path), json.dumps(node.skill_path),
            node.metadata.connection_strength_total, node.metadata.connected_memory_count,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_connection(self, connection: MemoryConnection):
        """Save memory connection to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        connection_id = f"{connection.source_memory_id}->{connection.target_memory_id}"
        
        cursor.execute('''
            INSERT OR REPLACE INTO brain_memory_connections (
                id, source_memory_id, target_memory_id, connection_type,
                strength, last_reinforced, reinforcement_count, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            connection_id, connection.source_memory_id, connection.target_memory_id,
            connection.connection_type.value, connection.strength,
            connection.last_reinforced, connection.reinforcement_count,
            json.dumps(connection.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    async def _load_memories(self):
        """Load existing memories from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM brain_memory_nodes')
            rows = cursor.fetchall()
            
            for row in rows:
                # Reconstruct MemoryNode from database
                node = MemoryNode(
                    id=row[0],
                    content="",  # Will be loaded from original memories table
                    memory_type="",  # Will be loaded from original memories table  
                    project_id="",  # Will be loaded from original memories table
                    tags=[]  # Will be loaded from original memories table
                )
                
                # Load metadata
                node.metadata = MemoryMetadata(
                    access_count=row[3],
                    last_accessed=datetime.fromisoformat(row[4]),
                    emotional_weight=row[6],
                    integration_depth=row[7],
                    decay_rate=row[8],
                    reinforcement_count=row[9],
                    memory_layer=MemoryLayer(row[1]),
                    memory_state=MemoryState(row[2]),
                    topic_categories=json.loads(row[10]) if row[10] else [],
                    skill_categories=json.loads(row[11]) if row[11] else [],
                    context_categories=json.loads(row[12]) if row[12] else []
                )
                
                node.topic_path = json.loads(row[13]) if row[13] else []
                node.skill_path = json.loads(row[14]) if row[14] else []
                
                self.memory_nodes[node.id] = node
        
        except sqlite3.OperationalError:
            # Table doesn't exist yet, that's okay
            pass
        
        conn.close()
    
    async def get_memory_insights(self, project_id: str = None) -> Dict[str, Any]:
        """Get insights about memory patterns and knowledge growth."""
        insights = {
            "memory_distribution": defaultdict(int),
            "layer_distribution": defaultdict(int),
            "state_distribution": defaultdict(int),
            "top_topics": defaultdict(int),
            "top_skills": defaultdict(int),
            "connection_patterns": defaultdict(int),
            "knowledge_growth": [],
            "recommendations": []
        }
        
        # Filter by project if specified
        memories = [node for node in self.memory_nodes.values() 
                   if not project_id or node.project_id == project_id]
        
        # Analyze distributions
        for node in memories:
            insights["layer_distribution"][node.metadata.memory_layer.value] += 1
            insights["state_distribution"][node.metadata.memory_state.value] += 1
            
            for topic in node.metadata.topic_categories:
                insights["top_topics"][topic] += 1
            
            for skill in node.metadata.skill_categories:
                insights["top_skills"][skill] += 1
        
        # Analyze connections
        for source_id, connections in self.connections.items():
            for target_id, connection in connections.items():
                insights["connection_patterns"][connection.connection_type.value] += 1
        
        # Generate recommendations
        if insights["layer_distribution"]["short_term"] > self.config["short_term_limit"]:
            insights["recommendations"].append(
                "Consider consolidating short-term memories - you have many temporary items"
            )
        
        if insights["state_distribution"]["dormant"] > len(memories) * 0.3:
            insights["recommendations"].append(
                "Many memories are dormant - consider reviewing and updating relevant knowledge"
            )
        
        return insights