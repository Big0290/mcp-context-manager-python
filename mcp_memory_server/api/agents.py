"""
Agents API endpoints for managing AI agent identities.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from mcp_memory_server.database.base import get_db
from mcp_memory_server.models.agent import (
    Agent,
    AgentCreate,
    AgentResponse,
    AgentStats,
    AgentSummary,
    AgentUpdate,
)
from mcp_memory_server.models.memory import Memory

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("/register", response_model=AgentResponse)
async def register_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Register a new agent."""
    try:
        # Check if agent name already exists
        existing_agent = db.query(Agent).filter(Agent.name == agent_data.name).first()
        if existing_agent:
            raise HTTPException(status_code=400, detail="Agent name already exists")

        # Create new agent
        agent = Agent(
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            project_id=agent_data.project_id,
            custom_metadata=agent_data.custom_metadata,
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        return AgentResponse.from_orm(agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to register agent: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: UUID, db: Session = Depends(get_db)):
    """Get agent information by ID."""
    try:
        agent = (
            db.query(Agent)
            .filter(and_(Agent.id == agent_id, Agent.is_active == True))
            .first()
        )

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        return AgentResponse.from_orm(agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID, update_data: AgentUpdate, db: Session = Depends(get_db)
):
    """Update agent information."""
    try:
        agent = (
            db.query(Agent)
            .filter(and_(Agent.id == agent_id, Agent.is_active == True))
            .first()
        )

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(agent, field, value)

        db.commit()
        db.refresh(agent)

        return AgentResponse.from_orm(agent)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")


@router.get("/", response_model=List[AgentSummary])
async def list_agents(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    """List all agents with optional filtering."""
    try:
        query = db.query(Agent).filter(Agent.is_active == True)

        if project_id:
            query = query.filter(Agent.project_id == project_id)

        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)

        agents = query.order_by(desc(Agent.last_seen)).limit(limit).all()

        # Get memory counts for each agent
        agent_summaries = []
        for agent in agents:
            memory_count = (
                db.query(Memory)
                .filter(and_(Memory.agent_id == agent.id, Memory.is_deleted == False))
                .count()
            )

            summary = AgentSummary(
                id=agent.id,
                name=agent.name,
                agent_type=agent.agent_type,
                project_id=agent.project_id,
                memory_count=memory_count,
                last_seen=agent.last_seen,
                is_active=agent.is_active,
            )
            agent_summaries.append(summary)

        return agent_summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/{agent_id}/stats", response_model=AgentStats)
async def get_agent_stats(agent_id: UUID, db: Session = Depends(get_db)):
    """Get detailed statistics for an agent."""
    try:
        # Get agent
        agent = (
            db.query(Agent)
            .filter(and_(Agent.id == agent_id, Agent.is_active == True))
            .first()
        )

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Get memories
        memories = (
            db.query(Memory)
            .filter(and_(Memory.agent_id == agent_id, Memory.is_deleted == False))
            .all()
        )

        # Calculate statistics
        total_memories = len(memories)
        short_term_memories = len([m for m in memories if m.is_short_term])
        long_term_memories = total_memories - short_term_memories

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

        # Get recent activity
        recent_memories = (
            db.query(Memory)
            .filter(and_(Memory.agent_id == agent_id, Memory.is_deleted == False))
            .order_by(desc(Memory.created_at))
            .limit(10)
            .all()
        )

        recent_activity = []
        for memory in recent_memories:
            recent_activity.append(
                {
                    "id": str(memory.id),
                    "type": memory.memory_type,
                    "content": memory.content[:100] + "..."
                    if len(memory.content) > 100
                    else memory.content,
                    "created_at": memory.created_at.isoformat(),
                    "tags": memory.tags,
                }
            )

        stats = AgentStats(
            total_memories=total_memories,
            short_term_memories=short_term_memories,
            long_term_memories=long_term_memories,
            memory_types=memory_types,
            top_tags=[{"tag": tag, "count": count} for tag, count in top_tags],
            recent_activity=recent_activity,
        )

        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get agent stats: {str(e)}"
        )


@router.post("/{agent_id}/ping")
async def ping_agent(agent_id: UUID, db: Session = Depends(get_db)):
    """Update agent's last seen timestamp."""
    try:
        agent = (
            db.query(Agent)
            .filter(and_(Agent.id == agent_id, Agent.is_active == True))
            .first()
        )

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        from datetime import datetime

        agent.last_seen = datetime.utcnow()
        db.commit()

        return {"message": "Agent pinged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ping agent: {str(e)}")


@router.delete("/{agent_id}")
async def deactivate_agent(agent_id: UUID, db: Session = Depends(get_db)):
    """Deactivate an agent (soft delete)."""
    try:
        agent = (
            db.query(Agent)
            .filter(and_(Agent.id == agent_id, Agent.is_active == True))
            .first()
        )

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent.is_active = False
        db.commit()

        return {"message": "Agent deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to deactivate agent: {str(e)}"
        )
