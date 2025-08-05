#!/usr/bin/env python3
"""
Memory Cross-Referencing Engine for Brain-Like MCP Server
Supports querying prior tasks by tags, structure similarity, and goal type.
"""

import json
import logging
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class QueryResult:
    """Represents a query result with relevance scoring."""

    memory_id: str
    content: str
    relevance_score: float
    match_type: str
    match_details: Dict[str, Any]
    emotional_weight: float = 0.0
    last_accessed: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert query result to dictionary."""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "relevance_score": self.relevance_score,
            "match_type": self.match_type,
            "match_details": self.match_details,
            "emotional_weight": self.emotional_weight,
            "last_accessed": self.last_accessed.isoformat()
            if self.last_accessed
            else None,
        }


@dataclass
class QueryContext:
    """Context for memory queries."""

    query: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

    # Query parameters
    search_tags: List[str] = field(default_factory=list)
    goal_type: Optional[str] = None
    task_type: Optional[str] = None
    time_range_hours: Optional[int] = None

    # Search preferences
    include_emotional_weight: bool = True
    include_recent_memories: bool = True
    include_connected_memories: bool = True
    max_results: int = 20

    def to_dict(self) -> Dict[str, Any]:
        """Convert query context to dictionary."""
        return {
            "query": self.query,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "search_tags": self.search_tags,
            "goal_type": self.goal_type,
            "task_type": self.task_type,
            "time_range_hours": self.time_range_hours,
            "include_emotional_weight": self.include_emotional_weight,
            "include_recent_memories": self.include_recent_memories,
            "include_connected_memories": self.include_connected_memories,
            "max_results": self.max_results,
        }


class MemoryQueryEngine:
    """Advanced memory query engine with cross-referencing capabilities."""

    def __init__(self, brain_memory_system=None, experience_logger=None):
        self.logger = logging.getLogger(__name__)
        self.brain_memory_system = brain_memory_system
        self.experience_logger = experience_logger

        # Query cache for performance
        self.query_cache: Dict[str, Tuple[List[QueryResult], datetime]] = {}
        self.cache_timeout_hours = 1

        # Query statistics
        self.query_stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "average_response_time": 0.0,
        }

    def query_memories(
        self,
        query: str,
        project_id: str = None,
        search_tags: List[str] = None,
        goal_type: str = None,
        max_results: int = 20,
    ) -> List[QueryResult]:
        """Main query method for finding relevant memories."""
        import time

        start_time = time.time()

        # Create query context
        context = QueryContext(
            query=query,
            project_id=project_id,
            search_tags=search_tags or [],
            goal_type=goal_type,
            max_results=max_results,
        )

        # Check cache first
        cache_key = self._generate_cache_key(context)
        if cache_key in self.query_cache:
            cached_results, cache_time = self.query_cache[cache_key]
            if datetime.now() - cache_time < timedelta(hours=self.cache_timeout_hours):
                self.query_stats["cache_hits"] += 1
                self.logger.info(f"Cache hit for query: {query[:50]}...")
                return cached_results

        # Perform multi-strategy search
        results = []

        # Strategy 1: Direct content search
        content_results = self._search_by_content(query, context)
        results.extend(content_results)

        # Strategy 2: Tag-based search
        if search_tags:
            tag_results = self._search_by_tags(search_tags, context)
            results.extend(tag_results)

        # Strategy 3: Goal-based search
        if goal_type:
            goal_results = self._search_by_goal(goal_type, context)
            results.extend(goal_results)

        # Strategy 4: Structural similarity search
        structure_results = self._search_by_structure(query, context)
        results.extend(structure_results)

        # Strategy 5: Emotional weight search
        if context.include_emotional_weight:
            emotional_results = self._search_by_emotional_weight(context)
            results.extend(emotional_results)

        # Deduplicate and rank results
        unique_results = self._deduplicate_results(results)
        ranked_results = self._rank_results(unique_results, context)

        # Limit results
        final_results = ranked_results[:max_results]

        # Cache results
        self.query_cache[cache_key] = (final_results, datetime.now())

        # Update statistics
        response_time = time.time() - start_time
        self.query_stats["total_queries"] += 1
        self.query_stats["average_response_time"] = (
            self.query_stats["average_response_time"]
            * (self.query_stats["total_queries"] - 1)
            + response_time
        ) / self.query_stats["total_queries"]

        self.logger.info(
            f"Query completed in {response_time:.3f}s: {len(final_results)} results"
        )
        return final_results

    def _generate_cache_key(self, context: QueryContext) -> str:
        """Generate cache key for query context."""
        import hashlib

        context_str = json.dumps(context.to_dict(), sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def _search_by_content(
        self, query: str, context: QueryContext
    ) -> List[QueryResult]:
        """Search memories by content similarity."""
        if not self.brain_memory_system:
            return []

        try:
            # Use brain memory system's search capabilities
            memories = self.brain_memory_system.search_memories_with_context(
                query=query,
                project_id=context.project_id,
                focus_areas=context.search_tags,
            )

            results = []
            for memory in memories:
                # Calculate relevance score based on content similarity
                relevance_score = self._calculate_content_similarity(
                    query, memory.get("content", "")
                )

                if relevance_score > 0.1:  # Minimum relevance threshold
                    results.append(
                        QueryResult(
                            memory_id=memory.get("id", ""),
                            content=memory.get("content", ""),
                            relevance_score=relevance_score,
                            match_type="content_similarity",
                            match_details={"similarity_score": relevance_score},
                            emotional_weight=memory.get("emotional_weight", 0.0),
                            last_accessed=memory.get("last_accessed"),
                        )
                    )

            return results

        except Exception as e:
            self.logger.error(f"Error in content search: {e}")
            return []

    def _search_by_tags(
        self, tags: List[str], context: QueryContext
    ) -> List[QueryResult]:
        """Search memories by tag matching."""
        if not self.brain_memory_system:
            return []

        try:
            results = []

            # Get all memories for the project
            memories = self.brain_memory_system.search_memories_with_context(
                query="",  # Empty query to get all memories
                project_id=context.project_id,
            )

            for memory in memories:
                memory_tags = memory.get("tags", [])
                tag_matches = set(tags) & set(memory_tags)

                if tag_matches:
                    relevance_score = len(tag_matches) / len(tags)

                    results.append(
                        QueryResult(
                            memory_id=memory.get("id", ""),
                            content=memory.get("content", ""),
                            relevance_score=relevance_score,
                            match_type="tag_match",
                            match_details={"matched_tags": list(tag_matches)},
                            emotional_weight=memory.get("emotional_weight", 0.0),
                            last_accessed=memory.get("last_accessed"),
                        )
                    )

            return results

        except Exception as e:
            self.logger.error(f"Error in tag search: {e}")
            return []

    def _search_by_goal(
        self, goal_type: str, context: QueryContext
    ) -> List[QueryResult]:
        """Search memories by goal type."""
        if not self.brain_memory_system:
            return []

        try:
            # Search for memories that mention the goal type
            memories = self.brain_memory_system.search_memories_with_context(
                query=goal_type, project_id=context.project_id
            )

            results = []
            for memory in memories:
                # Check if the memory content contains goal-related keywords
                goal_keywords = self._get_goal_keywords(goal_type)
                content_lower = memory.get("content", "").lower()

                keyword_matches = sum(
                    1 for keyword in goal_keywords if keyword in content_lower
                )
                relevance_score = (
                    keyword_matches / len(goal_keywords) if goal_keywords else 0.0
                )

                if relevance_score > 0.2:  # Minimum threshold for goal relevance
                    results.append(
                        QueryResult(
                            memory_id=memory.get("id", ""),
                            content=memory.get("content", ""),
                            relevance_score=relevance_score,
                            match_type="goal_match",
                            match_details={
                                "goal_type": goal_type,
                                "keyword_matches": keyword_matches,
                            },
                            emotional_weight=memory.get("emotional_weight", 0.0),
                            last_accessed=memory.get("last_accessed"),
                        )
                    )

            return results

        except Exception as e:
            self.logger.error(f"Error in goal search: {e}")
            return []

    def _search_by_structure(
        self, query: str, context: QueryContext
    ) -> List[QueryResult]:
        """Search memories by structural similarity."""
        if not self.brain_memory_system:
            return []

        try:
            # Extract structural patterns from query
            query_patterns = self._extract_structural_patterns(query)

            memories = self.brain_memory_system.search_memories_with_context(
                query="", project_id=context.project_id
            )

            results = []
            for memory in memories:
                memory_content = memory.get("content", "")
                memory_patterns = self._extract_structural_patterns(memory_content)

                # Calculate structural similarity
                pattern_similarity = self._calculate_pattern_similarity(
                    query_patterns, memory_patterns
                )

                if pattern_similarity > 0.3:  # Higher threshold for structural matches
                    results.append(
                        QueryResult(
                            memory_id=memory.get("id", ""),
                            content=memory_content,
                            relevance_score=pattern_similarity,
                            match_type="structural_similarity",
                            match_details={"pattern_similarity": pattern_similarity},
                            emotional_weight=memory.get("emotional_weight", 0.0),
                            last_accessed=memory.get("last_accessed"),
                        )
                    )

            return results

        except Exception as e:
            self.logger.error(f"Error in structure search: {e}")
            return []

    def _search_by_emotional_weight(self, context: QueryContext) -> List[QueryResult]:
        """Search for emotionally significant memories."""
        if not self.brain_memory_system:
            return []

        try:
            memories = self.brain_memory_system.search_memories_with_context(
                query="", project_id=context.project_id
            )

            # Filter for high emotional weight memories
            high_emotional_memories = [
                memory
                for memory in memories
                if memory.get("emotional_weight", 0.0) > 0.7
            ]

            results = []
            for memory in high_emotional_memories:
                results.append(
                    QueryResult(
                        memory_id=memory.get("id", ""),
                        content=memory.get("content", ""),
                        relevance_score=memory.get("emotional_weight", 0.0),
                        match_type="emotional_significance",
                        match_details={
                            "emotional_weight": memory.get("emotional_weight", 0.0)
                        },
                        emotional_weight=memory.get("emotional_weight", 0.0),
                        last_accessed=memory.get("last_accessed"),
                    )
                )

            return results

        except Exception as e:
            self.logger.error(f"Error in emotional weight search: {e}")
            return []

    def _calculate_content_similarity(self, query: str, content: str) -> float:
        """Calculate content similarity between query and memory content."""
        if not query or not content:
            return 0.0

        # Simple word overlap similarity
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        intersection = query_words & content_words
        union = query_words | content_words

        return len(intersection) / len(union) if union else 0.0

    def _get_goal_keywords(self, goal_type: str) -> List[str]:
        """Get keywords associated with a goal type."""
        goal_keywords = {
            "debugging": [
                "error",
                "bug",
                "fix",
                "debug",
                "issue",
                "problem",
                "troubleshoot",
            ],
            "optimization": [
                "performance",
                "speed",
                "efficiency",
                "optimize",
                "improve",
                "faster",
            ],
            "learning": [
                "learn",
                "understand",
                "study",
                "research",
                "explore",
                "discover",
            ],
            "creation": [
                "create",
                "build",
                "develop",
                "implement",
                "design",
                "construct",
            ],
            "analysis": [
                "analyze",
                "examine",
                "investigate",
                "review",
                "assess",
                "evaluate",
            ],
            "testing": ["test", "verify", "validate", "check", "ensure", "confirm"],
        }

        return goal_keywords.get(goal_type.lower(), [goal_type])

    def _extract_structural_patterns(self, text: str) -> List[str]:
        """Extract structural patterns from text."""
        patterns = []

        # Code patterns
        if "def " in text or "class " in text or "import " in text:
            patterns.append("code_structure")

        # List patterns
        if re.search(r"\d+\.|[-*]\s", text):
            patterns.append("list_structure")

        # Question patterns
        if "?" in text or text.strip().startswith(
            ("what", "how", "why", "when", "where")
        ):
            patterns.append("question_structure")

        # Command patterns
        if re.search(r"^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\(", text, re.MULTILINE):
            patterns.append("command_structure")

        # Error patterns
        if any(
            word in text.lower() for word in ["error", "exception", "failed", "failed"]
        ):
            patterns.append("error_structure")

        return patterns

    def _calculate_pattern_similarity(
        self, patterns1: List[str], patterns2: List[str]
    ) -> float:
        """Calculate similarity between two sets of patterns."""
        if not patterns1 or not patterns2:
            return 0.0

        intersection = set(patterns1) & set(patterns2)
        union = set(patterns1) | set(patterns2)

        return len(intersection) / len(union) if union else 0.0

    def _deduplicate_results(self, results: List[QueryResult]) -> List[QueryResult]:
        """Remove duplicate results based on memory ID."""
        seen_ids = set()
        unique_results = []

        for result in results:
            if result.memory_id not in seen_ids:
                seen_ids.add(result.memory_id)
                unique_results.append(result)

        return unique_results

    def _rank_results(
        self, results: List[QueryResult], context: QueryContext
    ) -> List[QueryResult]:
        """Rank results by relevance and emotional weight."""
        for result in results:
            # Boost score for emotional weight if enabled
            if context.include_emotional_weight:
                result.relevance_score *= 1 + result.emotional_weight * 0.3

            # Boost score for recent memories if enabled
            if context.include_recent_memories and result.last_accessed:
                hours_since_access = (
                    datetime.now() - result.last_accessed
                ).total_seconds() / 3600
                if hours_since_access < 24:  # Recent within 24 hours
                    result.relevance_score *= 1.2

        # Sort by relevance score (descending)
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)

    def suggest_related_memories(
        self, memory_id: str, max_suggestions: int = 5
    ) -> List[QueryResult]:
        """Suggest related memories based on connections and similarity."""
        if not self.brain_memory_system:
            return []

        try:
            # Get connected memories
            connected_memories = self.brain_memory_system.search_memories_with_context(
                query="", project_id=None  # Search across all projects for connections
            )

            # Filter for memories that might be related
            related_results = []
            for memory in connected_memories:
                if memory.get("id") != memory_id:
                    # Calculate relationship score
                    relationship_score = self._calculate_relationship_score(
                        memory_id, memory
                    )

                    if relationship_score > 0.1:
                        related_results.append(
                            QueryResult(
                                memory_id=memory.get("id", ""),
                                content=memory.get("content", ""),
                                relevance_score=relationship_score,
                                match_type="related_memory",
                                match_details={
                                    "relationship_score": relationship_score
                                },
                                emotional_weight=memory.get("emotional_weight", 0.0),
                                last_accessed=memory.get("last_accessed"),
                            )
                        )

            # Sort and limit results
            related_results.sort(key=lambda x: x.relevance_score, reverse=True)
            return related_results[:max_suggestions]

        except Exception as e:
            self.logger.error(f"Error suggesting related memories: {e}")
            return []

    def _calculate_relationship_score(
        self, source_id: str, target_memory: Dict[str, Any]
    ) -> float:
        """Calculate relationship score between two memories."""
        # This is a simplified version - in a real implementation,
        # you would use the brain memory system's connection data
        return 0.5  # Placeholder score

    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query engine statistics."""
        return {
            "total_queries": self.query_stats["total_queries"],
            "cache_hits": self.query_stats["cache_hits"],
            "cache_hit_rate": (
                self.query_stats["cache_hits"] / self.query_stats["total_queries"]
                if self.query_stats["total_queries"] > 0
                else 0.0
            ),
            "average_response_time": self.query_stats["average_response_time"],
            "cache_size": len(self.query_cache),
        }

    def clear_cache(self):
        """Clear the query cache."""
        self.query_cache.clear()
        self.logger.info("Query cache cleared")

    def preload_frequent_queries(self, project_id: str = None):
        """Preload frequently used queries into cache."""
        if not self.brain_memory_system:
            return

        try:
            # Common query patterns
            common_queries = [
                "error",
                "bug",
                "fix",
                "problem",
                "how to",
                "what is",
                "why",
                "optimize",
                "improve",
                "performance",
                "test",
                "verify",
                "check",
            ]

            for query in common_queries:
                self.query_memories(query, project_id=project_id, max_results=5)

            self.logger.info(f"Preloaded {len(common_queries)} common queries")

        except Exception as e:
            self.logger.error(f"Error preloading queries: {e}")
