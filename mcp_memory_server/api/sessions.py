"""
Sessions API endpoints for tracking agent sessions and memory access patterns.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from mcp_memory_server.database.base import get_db
from mcp_memory_server.models.session import Session as SessionModel
from mcp_memory_server.models.session import (
    SessionCreate,
    SessionResponse,
    SessionUpdate,
)

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionResponse)
async def start_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """Start a new session for an agent."""
    try:
        session = SessionModel(
            agent_id=session_data.agent_id,
            memory_id=session_data.memory_id,
            session_type=session_data.session_type,
            custom_metadata=session_data.custom_metadata,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return SessionResponse.from_orm(session)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start session: {str(e)}"
        )


@router.put("/{session_id}/end", response_model=SessionResponse)
async def end_session(session_id: UUID, db: Session = Depends(get_db)):
    """End an active session."""
    try:
        session = (
            db.query(SessionModel)
            .filter(and_(SessionModel.id == session_id, SessionModel.is_active == True))
            .first()
        )

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session.ended_at = datetime.utcnow()
        session.is_active = False
        db.commit()
        db.refresh(session)

        return SessionResponse.from_orm(session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, db: Session = Depends(get_db)):
    """Get session information by ID."""
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse.from_orm(session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


@router.get("/agent/{agent_id}", response_model=List[SessionResponse])
async def get_agent_sessions(
    agent_id: UUID,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    db: Session = Depends(get_db),
):
    """Get sessions for a specific agent."""
    try:
        query = db.query(SessionModel).filter(SessionModel.agent_id == agent_id)

        if session_type:
            query = query.filter(SessionModel.session_type == session_type)

        sessions = query.order_by(desc(SessionModel.started_at)).limit(limit).all()

        return [SessionResponse.from_orm(session) for session in sessions]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get agent sessions: {str(e)}"
        )


@router.get("/active/agent/{agent_id}", response_model=List[SessionResponse])
async def get_active_sessions(agent_id: UUID, db: Session = Depends(get_db)):
    """Get active sessions for an agent."""
    try:
        sessions = (
            db.query(SessionModel)
            .filter(
                and_(SessionModel.agent_id == agent_id, SessionModel.is_active == True)
            )
            .order_by(desc(SessionModel.started_at))
            .all()
        )

        return [SessionResponse.from_orm(session) for session in sessions]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get active sessions: {str(e)}"
        )


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID, update_data: SessionUpdate, db: Session = Depends(get_db)
):
    """Update session information."""
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(session, field, value)

        db.commit()
        db.refresh(session)

        return SessionResponse.from_orm(session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update session: {str(e)}"
        )


@router.get("/stats/agent/{agent_id}")
async def get_session_stats(
    agent_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
):
    """Get session statistics for an agent."""
    try:
        from datetime import timedelta

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get sessions in date range
        sessions = (
            db.query(SessionModel)
            .filter(
                and_(
                    SessionModel.agent_id == agent_id,
                    SessionModel.started_at >= start_date,
                )
            )
            .all()
        )

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

        avg_duration = (
            total_duration / len(completed_sessions_with_duration)
            if completed_sessions_with_duration
            else 0
        )

        # Get recent sessions
        recent_sessions = (
            db.query(SessionModel)
            .filter(SessionModel.agent_id == agent_id)
            .order_by(desc(SessionModel.started_at))
            .limit(10)
            .all()
        )

        recent_activity = []
        for session in recent_sessions:
            recent_activity.append(
                {
                    "id": str(session.id),
                    "type": session.session_type,
                    "started_at": session.started_at.isoformat(),
                    "ended_at": session.ended_at.isoformat()
                    if session.ended_at
                    else None,
                    "is_active": session.is_active,
                }
            )

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "session_types": session_types,
            "average_duration_seconds": avg_duration,
            "recent_activity": recent_activity,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get session stats: {str(e)}"
        )
