"""
Session service for managing session operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from mcp_memory_server.models.session import (
    Session as SessionModel, SessionCreate, SessionUpdate, SessionResponse
)


class SessionService:
    """Service for managing session operations."""
    
    async def create_session(
        self, 
        db: Session, 
        session_data: SessionCreate
    ) -> SessionResponse:
        """Create a new session."""
        session = SessionModel(
            agent_id=session_data.agent_id,
            memory_id=session_data.memory_id,
            session_type=session_data.session_type,
            custom_metadata=session_data.custom_metadata
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return SessionResponse.from_orm(session)
    
    async def get_session(
        self, 
        db: Session, 
        session_id: UUID
    ) -> Optional[SessionResponse]:
        """Get session by ID."""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        return SessionResponse.from_orm(session) if session else None
    
    async def update_session(
        self, 
        db: Session, 
        session_id: UUID, 
        update_data: SessionUpdate
    ) -> Optional[SessionResponse]:
        """Update a session."""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        
        if not session:
            return None
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(session, field, value)
        
        db.commit()
        db.refresh(session)
        
        return SessionResponse.from_orm(session)
    
    async def end_session(
        self, 
        db: Session, 
        session_id: UUID
    ) -> Optional[SessionResponse]:
        """End an active session."""
        session = db.query(SessionModel).filter(
            and_(
                SessionModel.id == session_id,
                SessionModel.is_active == True
            )
        ).first()
        
        if not session:
            return None
        
        session.ended_at = datetime.utcnow()
        session.is_active = False
        db.commit()
        db.refresh(session)
        
        return SessionResponse.from_orm(session)
    
    async def get_agent_sessions(
        self, 
        db: Session, 
        agent_id: UUID,
        session_type: Optional[str] = None,
        limit: int = 50
    ) -> List[SessionResponse]:
        """Get sessions for a specific agent."""
        query = db.query(SessionModel).filter(SessionModel.agent_id == agent_id)
        
        if session_type:
            query = query.filter(SessionModel.session_type == session_type)
        
        sessions = query.order_by(desc(SessionModel.started_at)).limit(limit).all()
        
        return [SessionResponse.from_orm(session) for session in sessions]
    
    async def get_active_sessions(
        self, 
        db: Session, 
        agent_id: UUID
    ) -> List[SessionResponse]:
        """Get active sessions for an agent."""
        sessions = db.query(SessionModel).filter(
            and_(
                SessionModel.agent_id == agent_id,
                SessionModel.is_active == True
            )
        ).order_by(desc(SessionModel.started_at)).all()
        
        return [SessionResponse.from_orm(session) for session in sessions]
    
    async def get_session_stats(
        self, 
        db: Session, 
        agent_id: UUID,
        days: int = 30
    ) -> dict:
        """Get session statistics for an agent."""
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get sessions in date range
        sessions = db.query(SessionModel).filter(
            and_(
                SessionModel.agent_id == agent_id,
                SessionModel.started_at >= start_date
            )
        ).all()
        
        # Calculate statistics
        total_sessions = len(sessions)
        active_sessions = len([s for s in sessions if s.is_active])
        completed_sessions = total_sessions - active_sessions
        
        # Count by session type
        session_types = {}
        for session in sessions:
            session_type = session.session_type
            session_types[session_type] = session_types.get(session_type, 0) + 1
        
        # Calculate average session duration
        completed_sessions_with_duration = [
            s for s in sessions if s.ended_at and s.started_at
        ]
        
        total_duration = 0
        for session in completed_sessions_with_duration:
            duration = session.ended_at - session.started_at
            total_duration += duration.total_seconds()
        
        avg_duration = total_duration / len(completed_sessions_with_duration) if completed_sessions_with_duration else 0
        
        # Get recent sessions
        recent_sessions = db.query(SessionModel).filter(
            SessionModel.agent_id == agent_id
        ).order_by(desc(SessionModel.started_at)).limit(10).all()
        
        recent_activity = []
        for session in recent_sessions:
            recent_activity.append({
                "id": str(session.id),
                "type": session.session_type,
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "is_active": session.is_active
            })
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "session_types": session_types,
            "average_duration_seconds": avg_duration,
            "recent_activity": recent_activity
        } 