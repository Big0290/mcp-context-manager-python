"""
Memory API endpoints for CRUD operations on memories.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from mcp_memory_server.database.base import get_db
from mcp_memory_server.models.memory import (
    MemoryCreate, MemoryUpdate, MemorySearch, MemoryResponse, MemorySummary
)
from mcp_memory_server.core.memory_engine import MemoryEngine
from mcp_memory_server.core.embedding_service import EmbeddingService

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


def get_memory_engine() -> MemoryEngine:
    """Dependency to get memory engine."""
    embedding_service = EmbeddingService()
    return MemoryEngine(embedding_service)


@router.post("/push", response_model=MemoryResponse)
async def push_memory(
    memory_data: MemoryCreate,
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Push a new memory to the server."""
    try:
        memory = await memory_engine.create_memory(db, memory_data)
        return memory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create memory: {str(e)}")


@router.get("/fetch", response_model=List[MemoryResponse])
async def fetch_memories(
    agent_id: UUID = Query(..., description="Agent ID"),
    query: Optional[str] = Query(None, description="Search query"),
    memory_type: Optional[str] = Query(None, description="Memory type filter"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    min_similarity: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Fetch memories for an agent with optional search and filtering."""
    try:
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        search_params = MemorySearch(
            agent_id=agent_id,
            query=query,
            memory_type=memory_type,
            tags=tag_list,
            limit=limit,
            min_similarity=min_similarity
        )
        
        memories = await memory_engine.search_memories(db, search_params)
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch memories: {str(e)}")


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Get a specific memory by ID."""
    try:
        memory = await memory_engine.get_memory(db, memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return memory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory: {str(e)}")


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: UUID,
    update_data: MemoryUpdate,
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Update an existing memory."""
    try:
        memory = await memory_engine.update_memory(db, memory_id, update_data)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return memory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update memory: {str(e)}")


@router.post("/{memory_id}/tag")
async def tag_memory(
    memory_id: UUID,
    tags: List[str],
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Add tags to a memory."""
    try:
        update_data = MemoryUpdate(tags=tags)
        memory = await memory_engine.update_memory(db, memory_id, update_data)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"message": "Tags updated successfully", "memory": memory}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to tag memory: {str(e)}")


@router.post("/{memory_id}/forget")
async def forget_memory(
    memory_id: UUID,
    reason: str = "User request",
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Soft delete a memory."""
    try:
        success = await memory_engine.delete_memory(db, memory_id, reason)
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"message": "Memory forgotten successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to forget memory: {str(e)}")


@router.get("/agent/{agent_id}/recent", response_model=List[MemoryResponse])
async def get_recent_memories(
    agent_id: UUID,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Get recent memories for an agent."""
    try:
        memories = await memory_engine.get_agent_memories(db, agent_id, limit)
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent memories: {str(e)}")


@router.get("/project/{project_id}", response_model=List[MemoryResponse])
async def get_project_memories(
    project_id: str,
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Get memories for a specific project."""
    try:
        memories = await memory_engine.get_project_memories(db, project_id, limit)
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project memories: {str(e)}")


@router.post("/agent/{agent_id}/summarize")
async def summarize_agent_memories(
    agent_id: UUID,
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Trigger auto-summarization for an agent's memories."""
    try:
        summary = await memory_engine.auto_summarize_memories(db, agent_id)
        if summary:
            return {"message": "Summary created successfully", "summary": summary}
        else:
            return {"message": "No summarization needed at this time"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize memories: {str(e)}")


@router.get("/stats/agent/{agent_id}")
async def get_agent_memory_stats(
    agent_id: UUID,
    db: Session = Depends(get_db),
    memory_engine: MemoryEngine = Depends(get_memory_engine)
):
    """Get memory statistics for an agent."""
    try:
        # Get recent memories for stats
        memories = await memory_engine.get_agent_memories(db, agent_id, 1000)
        
        # Calculate statistics
        total_count = len(memories)
        short_term_count = len([m for m in memories if m.is_short_term])
        long_term_count = total_count - short_term_count
        
        # Count by memory type
        memory_types = {}
        for memory in memories:
            memory_type = memory.memory_type
            memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
        
        # Get top tags
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_memories": total_count,
            "short_term_memories": short_term_count,
            "long_term_memories": long_term_count,
            "memory_types": memory_types,
            "top_tags": [{"tag": tag, "count": count} for tag, count in top_tags]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get memory stats: {str(e)}") 