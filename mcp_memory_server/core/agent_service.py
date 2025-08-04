"""
Agent service for managing agent operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from mcp_memory_server.models.agent import (
    Agent, AgentCreate, AgentUpdate, AgentResponse, AgentSummary, AgentStats
)
from mcp_memory_server.models.memory import Memory


class AgentService:
    """Service for managing agent operations."""
    
    async def create_agent(
        self, 
        db: Session, 
        agent_data: AgentCreate
    ) -> AgentResponse:
        """Create a new agent."""
        # Check if agent name already exists
        existing_agent = db.query(Agent).filter(Agent.name == agent_data.name).first()
        if existing_agent:
            raise ValueError("Agent name already exists")
        
        # Create new agent
        agent = Agent(
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            project_id=agent_data.project_id,
            custom_metadata=agent_data.custom_metadata
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        return AgentResponse.from_orm(agent)
    
    async def get_agent(
        self, 
        db: Session, 
        agent_id: UUID
    ) -> Optional[AgentResponse]:
        """Get agent by ID."""
        agent = db.query(Agent).filter(
            and_(
                Agent.id == agent_id,
                Agent.is_active == True
            )
        ).first()
        
        return AgentResponse.from_orm(agent) if agent else None
    
    async def update_agent(
        self, 
        db: Session, 
        agent_id: UUID, 
        update_data: AgentUpdate
    ) -> Optional[AgentResponse]:
        """Update an agent."""
        agent = db.query(Agent).filter(
            and_(
                Agent.id == agent_id,
                Agent.is_active == True
            )
        ).first()
        
        if not agent:
            return None
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(agent, field, value)
        
        db.commit()
        db.refresh(agent)
        
        return AgentResponse.from_orm(agent)
    
    async def list_agents(
        self, 
        db: Session, 
        project_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        limit: int = 50
    ) -> List[AgentSummary]:
        """List agents with optional filtering."""
        query = db.query(Agent).filter(Agent.is_active == True)
        
        if project_id:
            query = query.filter(Agent.project_id == project_id)
        
        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)
        
        agents = query.order_by(desc(Agent.last_seen)).limit(limit).all()
        
        # Get memory counts for each agent
        agent_summaries = []
        for agent in agents:
            memory_count = db.query(Memory).filter(
                and_(
                    Memory.agent_id == agent.id,
                    Memory.is_deleted == False
                )
            ).count()
            
            summary = AgentSummary(
                id=agent.id,
                name=agent.name,
                agent_type=agent.agent_type,
                project_id=agent.project_id,
                memory_count=memory_count,
                last_seen=agent.last_seen,
                is_active=agent.is_active
            )
            agent_summaries.append(summary)
        
        return agent_summaries
    
    async def get_agent_stats(
        self, 
        db: Session, 
        agent_id: UUID
    ) -> Optional[AgentStats]:
        """Get detailed statistics for an agent."""
        # Get agent
        agent = db.query(Agent).filter(
            and_(
                Agent.id == agent_id,
                Agent.is_active == True
            )
        ).first()
        
        if not agent:
            return None
        
        # Get memories
        memories = db.query(Memory).filter(
            and_(
                Memory.agent_id == agent_id,
                Memory.is_deleted == False
            )
        ).all()
        
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
        recent_memories = db.query(Memory).filter(
            and_(
                Memory.agent_id == agent_id,
                Memory.is_deleted == False
            )
        ).order_by(desc(Memory.created_at)).limit(10).all()
        
        recent_activity = []
        for memory in recent_memories:
            recent_activity.append({
                "id": str(memory.id),
                "type": memory.memory_type,
                "content": memory.content[:100] + "..." if len(memory.content) > 100 else memory.content,
                "created_at": memory.created_at.isoformat(),
                "tags": memory.tags
            })
        
        stats = AgentStats(
            total_memories=total_memories,
            short_term_memories=short_term_memories,
            long_term_memories=long_term_memories,
            memory_types=memory_types,
            top_tags=[{"tag": tag, "count": count} for tag, count in top_tags],
            recent_activity=recent_activity
        )
        
        return stats
    
    async def ping_agent(
        self, 
        db: Session, 
        agent_id: UUID
    ) -> bool:
        """Update agent's last seen timestamp."""
        agent = db.query(Agent).filter(
            and_(
                Agent.id == agent_id,
                Agent.is_active == True
            )
        ).first()
        
        if not agent:
            return False
        
        agent.last_seen = datetime.utcnow()
        db.commit()
        
        return True
    
    async def deactivate_agent(
        self, 
        db: Session, 
        agent_id: UUID
    ) -> bool:
        """Deactivate an agent (soft delete)."""
        agent = db.query(Agent).filter(
            and_(
                Agent.id == agent_id,
                Agent.is_active == True
            )
        ).first()
        
        if not agent:
            return False
        
        agent.is_active = False
        db.commit()
        
        return True 