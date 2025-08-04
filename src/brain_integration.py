#!/usr/bin/env python3
"""
Brain Integration Layer for MCP Context Manager
Seamlessly integrates brain-like memory system with existing MCP server functionality.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .brain_memory_system import (
    BrainMemorySystem,
    ConnectionType,
    MemoryLayer,
    MemoryMetadata,
    MemoryNode,
    MemoryState,
)


class BrainIntegration:
    """
    Integration layer that enhances existing MCP server with brain-like memory capabilities.
    Preserves all existing functionality while adding new brain features.
    """

    def __init__(self, original_mcp_server, enable_brain_features: bool = True):
        self.original_server = original_mcp_server
        self.enable_brain_features = enable_brain_features
        self.logger = logging.getLogger(__name__)

        # Initialize brain memory system if enabled
        if self.enable_brain_features:
            self.brain_system = BrainMemorySystem(
                db_path=str(
                    Path(original_mcp_server.db_path).parent / "brain_memory.db"
                ),
                embedding_service=getattr(
                    original_mcp_server, "embedding_service", None
                ),
            )
        else:
            self.brain_system = None

    def get_enhanced_tools(self) -> List[Dict[str, Any]]:
        """
        Get tools list with brain enhancements while preserving all original tools.
        """
        # Start with all original tools
        tools = self.original_server.get_tools()

        if not self.enable_brain_features:
            return tools

        # Add brain-enhanced tools
        brain_tools = [
            {
                "name": "search_similar_experiences",
                "description": "Find similar past experiences and related knowledge using brain-like memory search",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for finding similar experiences",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier to search within",
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas to focus on (topics, skills, technologies)",
                        },
                        "include_analogies": {
                            "type": "boolean",
                            "description": "Include analogical reasoning from similar patterns",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_knowledge_graph",
                "description": "Get interconnected knowledge graph for a topic or project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "center_topic": {
                            "type": "string",
                            "description": "Central topic to build graph around",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier",
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum connection depth (default: 2)",
                        },
                        "connection_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of connections to include",
                        },
                    },
                    "required": ["center_topic"],
                },
            },
            {
                "name": "get_memory_insights",
                "description": "Get insights about knowledge patterns, growth, and recommendations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project identifier for focused insights",
                        },
                        "include_recommendations": {
                            "type": "boolean",
                            "description": "Include AI recommendations for knowledge management",
                        },
                    },
                },
            },
            {
                "name": "promote_memory_knowledge",
                "description": "Manually promote important memories and update knowledge structures",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "memory_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Memory IDs to promote",
                        },
                        "target_layer": {
                            "type": "string",
                            "enum": [
                                "short_term",
                                "long_term",
                                "episodic",
                                "procedural",
                                "semantic",
                            ],
                            "description": "Target memory layer",
                        },
                        "emotional_weight": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Importance weight (0.0 to 1.0)",
                        },
                    },
                    "required": ["memory_ids"],
                },
            },
            {
                "name": "trace_knowledge_path",
                "description": "Trace how knowledge flows from one concept to another through memory connections",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "from_concept": {
                            "type": "string",
                            "description": "Starting concept or memory",
                        },
                        "to_concept": {
                            "type": "string",
                            "description": "Target concept or memory",
                        },
                        "max_hops": {
                            "type": "integer",
                            "description": "Maximum number of connection hops (default: 5)",
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project context for search",
                        },
                    },
                    "required": ["from_concept", "to_concept"],
                },
            },
        ]

        return tools + brain_tools

    async def execute_enhanced_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tools with brain enhancements while preserving original functionality.
        """
        # Handle brain-specific tools
        if self.enable_brain_features and tool_name in [
            "search_similar_experiences",
            "get_knowledge_graph",
            "get_memory_insights",
            "promote_memory_knowledge",
            "trace_knowledge_path",
        ]:
            return await self._execute_brain_tool(tool_name, arguments)

        # For original tools, enhance with brain features if enabled
        if tool_name == "push_memory":
            result = await self.original_server._push_memory(arguments)

            # Enhance with brain processing
            if self.enable_brain_features and not result.get("isError", True):
                await self._enhance_pushed_memory(arguments, result)

            return result

        elif tool_name == "fetch_memory":
            # Use brain-enhanced search if available
            if self.enable_brain_features:
                return await self._fetch_memory_enhanced(arguments)
            else:
                return await self.original_server._fetch_memory(arguments)

        elif tool_name == "get_context_summary":
            # Use brain-enhanced context if available
            if self.enable_brain_features:
                return await self._get_context_summary_enhanced(arguments)
            else:
                return await self.original_server._get_context_summary(arguments)

        else:
            # Execute original tool without modification
            return await self.original_server.execute_tool(tool_name, arguments)

    async def _execute_brain_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute brain-specific tools."""
        try:
            if tool_name == "search_similar_experiences":
                return await self._search_similar_experiences(arguments)

            elif tool_name == "get_knowledge_graph":
                return await self._get_knowledge_graph(arguments)

            elif tool_name == "get_memory_insights":
                return await self._get_memory_insights(arguments)

            elif tool_name == "promote_memory_knowledge":
                return await self._promote_memory_knowledge(arguments)

            elif tool_name == "trace_knowledge_path":
                return await self._trace_knowledge_path(arguments)

            else:
                return {"error": f"Unknown brain tool: {tool_name}"}

        except Exception as e:
            self.logger.error(f"Error executing brain tool {tool_name}: {e}")
            return {"error": f"Brain tool execution failed: {str(e)}"}

    async def _enhance_pushed_memory(
        self, arguments: Dict[str, Any], result: Dict[str, Any]
    ):
        """Enhance a newly pushed memory with brain features."""
        if not self.brain_system:
            return

        try:
            # Extract memory ID from result
            result_text = result.get("content", [{}])[0].get("text", "")
            if "ID:" in result_text:
                memory_id = result_text.split("ID:")[1].strip().split()[0]

                # Enhance the memory with brain features
                memory_data = {
                    "content": arguments.get("content", ""),
                    "memory_type": arguments.get("memory_type", "fact"),
                    "project_id": arguments.get("project_id", "default"),
                    "tags": arguments.get("tags", []),
                    "priority": arguments.get("priority", "medium"),
                }

                await self.brain_system.enhance_existing_memory(memory_id, memory_data)

        except Exception as e:
            self.logger.error(f"Error enhancing pushed memory: {e}")

    async def _fetch_memory_enhanced(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch memories with brain-enhanced search."""
        query = arguments.get("query", "")
        project_id = arguments.get("project_id", "default")
        focus_areas = arguments.get("focus_areas", [])

        # Use brain search if query is substantial
        if query and len(query) > 5 and self.brain_system:
            brain_results = await self.brain_system.search_memories_with_context(
                query=query, project_id=project_id, focus_areas=focus_areas
            )

            if brain_results:
                # Format brain results for MCP response
                formatted_results = []
                for result in brain_results[:10]:  # Limit to top 10
                    node = result["node"]
                    formatted_results.append(
                        {
                            "id": result["memory_id"],
                            "content": node.content,
                            "memory_type": node.memory_type,
                            "tags": node.tags,
                            "project_id": node.project_id,
                            "similarity_score": result["score"],
                            "match_type": result["match_type"],
                            "memory_layer": node.metadata.memory_layer.value,
                            "emotional_weight": node.metadata.emotional_weight,
                            "access_count": node.metadata.access_count,
                        }
                    )

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"🧠 **Brain-Enhanced Search Results** ({len(formatted_results)} found):\n\n"
                            + json.dumps(formatted_results, indent=2, default=str),
                        }
                    ],
                    "isError": False,
                }

        # Fallback to original search
        return await self.original_server._fetch_memory(arguments)

    async def _get_context_summary_enhanced(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get context summary with brain-enhanced insights."""
        # Get original context summary
        original_result = await self.original_server._get_context_summary(arguments)

        if not self.brain_system or original_result.get("isError", False):
            return original_result

        try:
            project_id = arguments.get("project_id", "default")

            # Get brain insights
            insights = await self.brain_system.get_memory_insights(project_id)

            # Get original summary text
            original_text = original_result.get("content", [{}])[0].get("text", "")

            # Add brain insights
            brain_insights_text = "\n\n🧠 **Memory Insights:**\n"
            brain_insights_text += (
                f"• Memory Layers: {dict(insights['layer_distribution'])}\n"
            )
            brain_insights_text += (
                f"• Memory States: {dict(insights['state_distribution'])}\n"
            )
            brain_insights_text += (
                f"• Top Topics: {dict(list(insights['top_topics'].items())[:3])}\n"
            )
            brain_insights_text += (
                f"• Connection Types: {dict(insights['connection_patterns'])}\n"
            )

            if insights["recommendations"]:
                brain_insights_text += "\n💡 **Recommendations:**\n"
                for rec in insights["recommendations"][:3]:
                    brain_insights_text += f"• {rec}\n"

            enhanced_text = original_text + brain_insights_text

            return {
                "content": [{"type": "text", "text": enhanced_text}],
                "isError": False,
            }

        except Exception as e:
            self.logger.error(f"Error enhancing context summary: {e}")
            return original_result

    async def _search_similar_experiences(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Search for similar experiences using brain memory system."""
        query = arguments.get("query", "")
        project_id = arguments.get("project_id")
        focus_areas = arguments.get("focus_areas", [])
        include_analogies = arguments.get("include_analogies", True)

        if not query:
            return {"error": "Query is required for experience search"}

        try:
            results = await self.brain_system.search_memories_with_context(
                query=query, project_id=project_id, focus_areas=focus_areas
            )

            # Categorize results
            direct_matches = [r for r in results if r["match_type"] == "direct"]
            similar_experiences = [r for r in results if "similar" in r["match_type"]]
            connected_knowledge = [r for r in results if "connected" in r["match_type"]]

            # Format response
            response_parts = []
            response_parts.append(
                f"🔍 **Similar Experience Search Results for:** '{query}'"
            )
            response_parts.append("")

            if direct_matches:
                response_parts.append("**🎯 Direct Matches:**")
                for result in direct_matches[:3]:
                    node = result["node"]
                    response_parts.append(
                        f"• [{node.metadata.memory_layer.value.upper()}] {node.content[:100]}..."
                    )
                    response_parts.append(
                        f"  Score: {result['score']:.2f} | Layer: {node.metadata.memory_layer.value}"
                    )
                response_parts.append("")

            if similar_experiences:
                response_parts.append("**🔄 Similar Experiences:**")
                for result in similar_experiences[:3]:
                    node = result["node"]
                    response_parts.append(
                        f"• [{node.metadata.memory_layer.value.upper()}] {node.content[:100]}..."
                    )
                    response_parts.append(
                        f"  Similarity: {result['score']:.2f} | Used {node.metadata.access_count}x"
                    )
                response_parts.append("")

            if connected_knowledge:
                response_parts.append("**🕸️ Connected Knowledge:**")
                for result in connected_knowledge[:3]:
                    node = result["node"]
                    response_parts.append(
                        f"• [{result['match_type'].upper()}] {node.content[:100]}..."
                    )
                    response_parts.append(f"  Connection: {result['score']:.2f}")
                response_parts.append("")

            if include_analogies:
                # Find analogical patterns
                analogies = await self._find_analogical_patterns(results)
                if analogies:
                    response_parts.append("**🔗 Analogical Patterns:**")
                    for pattern in analogies[:2]:
                        response_parts.append(f"• {pattern}")
                    response_parts.append("")

            return {
                "content": [{"type": "text", "text": "\n".join(response_parts)}],
                "isError": False,
            }

        except Exception as e:
            return {"error": f"Error searching similar experiences: {str(e)}"}

    async def _find_analogical_patterns(
        self, results: List[Dict[str, Any]]
    ) -> List[str]:
        """Find analogical patterns in search results."""
        patterns = []

        # Group by topic categories
        topic_groups = {}
        for result in results:
            node = result["node"]
            for topic in node.metadata.topic_categories:
                if topic not in topic_groups:
                    topic_groups[topic] = []
                topic_groups[topic].append(result)

        # Find cross-topic patterns
        for topic, topic_results in topic_groups.items():
            if len(topic_results) >= 2:
                patterns.append(
                    f"Similar patterns found in {topic}: "
                    f"{len(topic_results)} related experiences"
                )

        return patterns

    async def _get_knowledge_graph(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get interconnected knowledge graph."""
        center_topic = arguments.get("center_topic", "")
        project_id = arguments.get("project_id")
        max_depth = arguments.get("max_depth", 2)

        if not center_topic:
            return {"error": "Center topic is required for knowledge graph"}

        try:
            # Find memories related to center topic
            related_memories = await self.brain_system.search_memories_with_context(
                query=center_topic, project_id=project_id
            )

            # Build graph structure
            graph = {
                "center": center_topic,
                "nodes": [],
                "connections": [],
                "layers": {},
            }

            for result in related_memories[:15]:  # Limit nodes
                node = result["node"]
                graph["nodes"].append(
                    {
                        "id": result["memory_id"],
                        "content": node.content[:100] + "...",
                        "layer": node.metadata.memory_layer.value,
                        "weight": node.metadata.emotional_weight,
                        "access_count": node.metadata.access_count,
                        "topics": node.metadata.topic_categories[:3],
                    }
                )

                # Add to layer grouping
                layer = node.metadata.memory_layer.value
                if layer not in graph["layers"]:
                    graph["layers"][layer] = []
                graph["layers"][layer].append(result["memory_id"])

            # Add connections
            for memory_id in [r["memory_id"] for r in related_memories[:10]]:
                if memory_id in self.brain_system.connections:
                    for target_id, connection in self.brain_system.connections[
                        memory_id
                    ].items():
                        if any(n["id"] == target_id for n in graph["nodes"]):
                            graph["connections"].append(
                                {
                                    "from": memory_id,
                                    "to": target_id,
                                    "type": connection.connection_type.value,
                                    "strength": connection.strength,
                                }
                            )

            # Format response
            response_text = f"🕸️ **Knowledge Graph for '{center_topic}'**\n\n"
            response_text += f"**Nodes:** {len(graph['nodes'])}\n"
            response_text += f"**Connections:** {len(graph['connections'])}\n"
            response_text += f"**Layers:** {', '.join(graph['layers'].keys())}\n\n"

            # Show layer breakdown
            for layer, node_ids in graph["layers"].items():
                response_text += (
                    f"**{layer.title()} Layer:** {len(node_ids)} memories\n"
                )

            response_text += f"\n**Full Graph Data:**\n{json.dumps(graph, indent=2)}"

            return {
                "content": [{"type": "text", "text": response_text}],
                "isError": False,
            }

        except Exception as e:
            return {"error": f"Error building knowledge graph: {str(e)}"}

    async def _get_memory_insights(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory insights and recommendations."""
        project_id = arguments.get("project_id")
        include_recommendations = arguments.get("include_recommendations", True)

        try:
            insights = await self.brain_system.get_memory_insights(project_id)

            # Format insights
            response_parts = []
            response_parts.append("📊 **Memory System Insights**")
            response_parts.append("")

            # Memory distribution
            response_parts.append("**Memory Layer Distribution:**")
            for layer, count in insights["layer_distribution"].items():
                response_parts.append(f"• {layer.title()}: {count} memories")
            response_parts.append("")

            # Memory state distribution
            response_parts.append("**Memory State Distribution:**")
            for state, count in insights["state_distribution"].items():
                response_parts.append(f"• {state.title()}: {count} memories")
            response_parts.append("")

            # Top topics and skills
            if insights["top_topics"]:
                response_parts.append("**Top Knowledge Areas:**")
                for topic, count in list(insights["top_topics"].items())[:5]:
                    response_parts.append(f"• {topic}: {count} memories")
                response_parts.append("")

            # Connection patterns
            if insights["connection_patterns"]:
                response_parts.append("**Connection Patterns:**")
                for conn_type, count in insights["connection_patterns"].items():
                    response_parts.append(f"• {conn_type.title()}: {count} connections")
                response_parts.append("")

            # Recommendations
            if include_recommendations and insights["recommendations"]:
                response_parts.append("**💡 Recommendations:**")
                for rec in insights["recommendations"]:
                    response_parts.append(f"• {rec}")
                response_parts.append("")

            return {
                "content": [{"type": "text", "text": "\n".join(response_parts)}],
                "isError": False,
            }

        except Exception as e:
            return {"error": f"Error getting memory insights: {str(e)}"}

    async def _promote_memory_knowledge(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manually promote important memories."""
        memory_ids = arguments.get("memory_ids", [])
        target_layer = arguments.get("target_layer")
        emotional_weight = arguments.get("emotional_weight")

        if not memory_ids:
            return {"error": "Memory IDs are required for promotion"}

        try:
            promoted = []
            for memory_id in memory_ids:
                if memory_id in self.brain_system.memory_nodes:
                    node = self.brain_system.memory_nodes[memory_id]

                    # Update layer if specified
                    if target_layer:
                        node.metadata.memory_layer = MemoryLayer(target_layer)

                    # Update emotional weight if specified
                    if emotional_weight is not None:
                        node.metadata.emotional_weight = emotional_weight

                    # Promote memory state
                    node.metadata.memory_state = MemoryState.ACTIVE
                    node.metadata.access_count += 1
                    node.metadata.last_accessed = datetime.now()

                    # Save changes
                    await self.brain_system._save_memory_node(node)
                    promoted.append(memory_id)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ Successfully promoted {len(promoted)} memories:\n"
                        + f"• Memory IDs: {', '.join(promoted)}\n"
                        + f"• Target Layer: {target_layer or 'unchanged'}\n"
                        + f"• Emotional Weight: {emotional_weight or 'unchanged'}",
                    }
                ],
                "isError": False,
            }

        except Exception as e:
            return {"error": f"Error promoting memories: {str(e)}"}

    async def _trace_knowledge_path(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Trace knowledge flow between concepts."""
        from_concept = arguments.get("from_concept", "")
        to_concept = arguments.get("to_concept", "")
        max_hops = arguments.get("max_hops", 5)
        project_id = arguments.get("project_id")

        if not from_concept or not to_concept:
            return {"error": "Both from_concept and to_concept are required"}

        try:
            # Find memories for both concepts
            from_memories = await self.brain_system.search_memories_with_context(
                query=from_concept, project_id=project_id
            )
            to_memories = await self.brain_system.search_memories_with_context(
                query=to_concept, project_id=project_id
            )

            if not from_memories or not to_memories:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Could not find memories for both concepts:\n"
                            + f"• {from_concept}: {len(from_memories)} found\n"
                            + f"• {to_concept}: {len(to_memories)} found",
                        }
                    ],
                    "isError": False,
                }

            # Find shortest path using BFS
            paths = []
            start_ids = [r["memory_id"] for r in from_memories[:3]]
            end_ids = [r["memory_id"] for r in to_memories[:3]]

            for start_id in start_ids:
                for end_id in end_ids:
                    path = await self._find_shortest_path(start_id, end_id, max_hops)
                    if path:
                        paths.append(path)

            if not paths:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"🔍 **No direct knowledge path found between:**\n"
                            + f"• {from_concept}\n• {to_concept}\n\n"
                            + f"Consider creating connections by working with related concepts.",
                        }
                    ],
                    "isError": False,
                }

            # Format best path
            best_path = min(paths, key=len)

            response_parts = []
            response_parts.append(
                f"🛤️ **Knowledge Path: {from_concept} → {to_concept}**"
            )
            response_parts.append(f"Path length: {len(best_path) - 1} hops\n")

            for i, memory_id in enumerate(best_path):
                if memory_id in self.brain_system.memory_nodes:
                    node = self.brain_system.memory_nodes[memory_id]
                    arrow = " → " if i < len(best_path) - 1 else ""
                    response_parts.append(f"{i+1}. {node.content[:80]}...{arrow}")

            return {
                "content": [{"type": "text", "text": "\n".join(response_parts)}],
                "isError": False,
            }

        except Exception as e:
            return {"error": f"Error tracing knowledge path: {str(e)}"}

    async def _find_shortest_path(
        self, start_id: str, end_id: str, max_hops: int
    ) -> Optional[List[str]]:
        """Find shortest path between two memory nodes using BFS."""
        if start_id == end_id:
            return [start_id]

        visited = set()
        queue = [(start_id, [start_id])]

        while queue:
            current_id, path = queue.pop(0)

            if len(path) > max_hops:
                continue

            if current_id in visited:
                continue

            visited.add(current_id)

            # Check connections
            if current_id in self.brain_system.connections:
                for target_id, connection in self.brain_system.connections[
                    current_id
                ].items():
                    if target_id == end_id:
                        return path + [target_id]

                    if target_id not in visited and connection.strength > 0.3:
                        queue.append((target_id, path + [target_id]))

        return None

    async def run_memory_maintenance(self):
        """Run periodic memory maintenance tasks."""
        if not self.brain_system:
            return

        try:
            # Promote memory layers based on usage
            await self.brain_system.promote_memory_layers()

            # Clean up weak connections
            await self._cleanup_weak_connections()

            self.logger.info("Memory maintenance completed successfully")

        except Exception as e:
            self.logger.error(f"Error during memory maintenance: {e}")

    async def _cleanup_weak_connections(self):
        """Clean up connections that have become too weak."""
        threshold = self.brain_system.config["connection_strength_threshold"]

        for source_id, connections in list(self.brain_system.connections.items()):
            for target_id, connection in list(connections.items()):
                if connection.strength < threshold:
                    # Remove weak connection
                    del self.brain_system.connections[source_id][target_id]

                    # Update node metadata
                    if source_id in self.brain_system.memory_nodes:
                        node = self.brain_system.memory_nodes[source_id]
                        node.metadata.connected_memory_count -= 1
                        node.metadata.connection_strength_total -= connection.strength

                        # Save updated node
                        await self.brain_system._save_memory_node(node)
