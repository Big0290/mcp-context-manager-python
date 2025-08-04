"""
Core memory engine for handling memory operations, embeddings, and similarity search.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from mcp_memory_server.config import settings
from mcp_memory_server.core.embedding_service import EmbeddingService
from mcp_memory_server.models.memory import (
    Memory,
    MemoryCreate,
    MemoryResponse,
    MemorySearch,
    MemoryType,
    MemoryUpdate,
)


class MemoryEngine:
    """Core memory engine for managing agent memories."""

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    async def create_memory(
        self, db: Session, memory_data: MemoryCreate
    ) -> MemoryResponse:
        """Create a new memory entry."""
        # Create memory
        memory = Memory(
            agent_id=memory_data.agent_id,
            project_id=memory_data.project_id,
            content=memory_data.content,
            memory_type=memory_data.memory_type,
            priority=memory_data.priority,
            tags=memory_data.tags,
            custom_metadata=memory_data.custom_metadata,
            is_short_term=memory_data.is_short_term,
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        # Generate embedding if content is substantial
        if len(memory_data.content) > 10:
            await self._generate_embedding(db, memory)

        return MemoryResponse.from_orm(memory)

    async def get_memory(
        self, db: Session, memory_id: UUID
    ) -> Optional[MemoryResponse]:
        """Get a specific memory by ID."""
        memory = (
            db.query(Memory)
            .filter(and_(Memory.id == memory_id, Memory.is_deleted == False))
            .first()
        )

        return MemoryResponse.from_orm(memory) if memory else None

    async def search_memories(
        self, db: Session, search_params: MemorySearch
    ) -> List[MemoryResponse]:
        """Search memories using semantic similarity and filters."""
        query = db.query(Memory).filter(
            and_(Memory.agent_id == search_params.agent_id, Memory.is_deleted == False)
        )

        # Apply filters
        if search_params.memory_type:
            query = query.filter(Memory.memory_type == search_params.memory_type)

        if search_params.tags:
            # Search for memories that contain any of the specified tags
            tag_filters = [Memory.tags.contains([tag]) for tag in search_params.tags]
            query = query.filter(or_(*tag_filters))

        # If query is provided, use semantic search
        if search_params.query:
            memories = await self._semantic_search(
                db, query, search_params.query, search_params.limit
            )
        else:
            # Use regular database query
            memories = (
                query.order_by(desc(Memory.created_at)).limit(search_params.limit).all()
            )

        return [MemoryResponse.from_orm(memory) for memory in memories]

    async def update_memory(
        self, db: Session, memory_id: UUID, update_data: MemoryUpdate
    ) -> Optional[MemoryResponse]:
        """Update an existing memory."""
        memory = (
            db.query(Memory)
            .filter(and_(Memory.id == memory_id, Memory.is_deleted == False))
            .first()
        )

        if not memory:
            return None

        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(memory, field, value)

        memory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)

        # Regenerate embedding if content changed
        if update_data.content:
            await self._generate_embedding(db, memory)

        return MemoryResponse.from_orm(memory)

    async def delete_memory(
        self, db: Session, memory_id: UUID, reason: str = "User request"
    ) -> bool:
        """Soft delete a memory."""
        memory = (
            db.query(Memory)
            .filter(and_(Memory.id == memory_id, Memory.is_deleted == False))
            .first()
        )

        if not memory:
            return False

        memory.is_deleted = True
        memory.custom_metadata = {
            **memory.custom_metadata,
            "deletion_reason": reason,
            "deleted_at": datetime.utcnow().isoformat(),
        }
        db.commit()

        return True

    async def get_agent_memories(
        self, db: Session, agent_id: UUID, limit: int = 50
    ) -> List[MemoryResponse]:
        """Get recent memories for an agent."""
        memories = (
            db.query(Memory)
            .filter(and_(Memory.agent_id == agent_id, Memory.is_deleted == False))
            .order_by(desc(Memory.created_at))
            .limit(limit)
            .all()
        )

        return [MemoryResponse.from_orm(memory) for memory in memories]

    async def get_project_memories(
        self, db: Session, project_id: str, limit: int = 100
    ) -> List[MemoryResponse]:
        """Get memories for a specific project."""
        memories = (
            db.query(Memory)
            .filter(and_(Memory.project_id == project_id, Memory.is_deleted == False))
            .order_by(desc(Memory.created_at))
            .limit(limit)
            .all()
        )

        return [MemoryResponse.from_orm(memory) for memory in memories]

    async def _generate_embedding(self, db: Session, memory: Memory):
        """Generate embedding for a memory."""
        try:
            embedding_vector = await self.embedding_service.generate_embedding(
                memory.content
            )

            # Store embedding in memory record
            memory.embedding = embedding_vector
            db.commit()

        except Exception as e:
            # Log error but don't fail the operation
            print(f"Failed to generate embedding for memory {memory.id}: {e}")

    async def _semantic_search(
        self, db: Session, base_query, query_text: str, limit: int
    ) -> List[Memory]:
        """Perform semantic search using embeddings."""
        try:
            # Generate embedding for query
            query_embedding = await self.embedding_service.generate_embedding(
                query_text
            )

            # Get all memories that have embeddings
            memories = base_query.filter(Memory.embedding.isnot(None)).all()

            # Calculate similarities
            similarities = []
            for memory in memories:
                if memory.embedding:
                    similarity = self.embedding_service.calculate_similarity(
                        query_embedding, memory.embedding
                    )
                    if similarity >= settings.memory_relevancy_threshold:
                        similarities.append((memory, similarity))

            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [memory for memory, _ in similarities[:limit]]

        except Exception as e:
            print(f"Semantic search failed: {e}")
            # Fallback to regular search
            return base_query.order_by(desc(Memory.created_at)).limit(limit).all()

    async def auto_summarize_memories(
        self, db: Session, agent_id: UUID
    ) -> Optional[MemoryResponse]:
        """Automatically summarize old memories when threshold is reached."""
        # Count memories for this agent
        memory_count = (
            db.query(Memory)
            .filter(
                and_(
                    Memory.agent_id == agent_id,
                    Memory.is_deleted == False,
                    Memory.is_short_term == False,
                )
            )
            .count()
        )

        if memory_count >= settings.auto_summarize_threshold:
            # Get recent memories to summarize
            recent_memories = (
                db.query(Memory)
                .filter(
                    and_(
                        Memory.agent_id == agent_id,
                        Memory.is_deleted == False,
                        Memory.memory_type != MemoryType.SUMMARY,
                    )
                )
                .order_by(desc(Memory.created_at))
                .limit(20)
                .all()
            )

            if recent_memories:
                # Create summary content
                summary_content = await self._create_summary(recent_memories)

                # Create summary memory
                summary_memory = Memory(
                    agent_id=agent_id,
                    project_id=recent_memories[0].project_id,
                    content=summary_content,
                    memory_type=MemoryType.SUMMARY,
                    priority=3,  # High priority for summaries
                    tags=["auto_summary"],
                    custom_metadata={
                        "summarized_count": len(recent_memories),
                        "summarized_ids": [str(m.id) for m in recent_memories],
                    },
                    is_short_term=False,
                )

                db.add(summary_memory)
                db.commit()
                db.refresh(summary_memory)

                return MemoryResponse.from_orm(summary_memory)

        return None

    async def _create_summary(self, memories: List[Memory]) -> str:
        """Create a summary of multiple memories."""
        # Simple concatenation for now - could be enhanced with LLM summarization
        contents = [m.content for m in memories]
        summary = f"Summary of {len(memories)} recent memories:\n\n"
        summary += "\n".join([f"- {content[:100]}..." for content in contents[:5]])

        if len(contents) > 5:
            summary += f"\n... and {len(contents) - 5} more memories."

        return summary
