#!/usr/bin/env python3
"""
Performance Monitoring and Feedback System for Context Injection
Tracks usage patterns, performance metrics, and user feedback
"""

import json
import queue
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class PerformanceMonitor:
    def __init__(self, db_path: str = "performance_metrics.db"):
        self.db_path = db_path
        self.metrics_queue = queue.Queue()
        self.is_monitoring = False
        self.monitor_thread = None
        self._init_database()

    def _init_database(self):
        """Initialize the performance metrics database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                project_id TEXT,
                duration_ms REAL,
                success BOOLEAN,
                error_message TEXT,
                context_length INTEGER,
                memory_count INTEGER,
                user_feedback INTEGER,
                metadata TEXT
            )
        """
        )

        # Create feedback table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                rating INTEGER,
                comment TEXT,
                project_id TEXT,
                context_summary TEXT
            )
        """
        )

        # Create usage patterns table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                action_type TEXT,
                project_id TEXT,
                context_used BOOLEAN,
                manual_trigger BOOLEAN
            )
        """
        )

        conn.commit()
        conn.close()

    def start_monitoring(self):
        """Start the background monitoring thread."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True
            )
            self.monitor_thread.start()
            print("📊 Performance monitoring started")

    def stop_monitoring(self):
        """Stop the background monitoring thread."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("📊 Performance monitoring stopped")

    def _monitor_loop(self):
        """Background loop for processing metrics."""
        while self.is_monitoring:
            try:
                # Process metrics from queue
                while not self.metrics_queue.empty():
                    metric = self.metrics_queue.get_nowait()
                    self._store_metric(metric)

                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Error in monitoring loop: {e}")

    def track_event(
        self,
        event_type: str,
        project_id: str = None,
        duration_ms: float = None,
        success: bool = True,
        error_message: str = None,
        context_length: int = None,
        memory_count: int = None,
        metadata: Dict = None,
    ):
        """Track a performance event."""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "project_id": project_id,
            "duration_ms": duration_ms,
            "success": success,
            "error_message": error_message,
            "context_length": context_length,
            "memory_count": memory_count,
            "metadata": json.dumps(metadata) if metadata else None,
        }

        self.metrics_queue.put(metric)

    def _store_metric(self, metric: Dict[str, Any]):
        """Store a metric in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO performance_metrics
            (timestamp, event_type, project_id, duration_ms, success,
             error_message, context_length, memory_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metric["timestamp"],
                metric["event_type"],
                metric["project_id"],
                metric["duration_ms"],
                metric["success"],
                metric["error_message"],
                metric["context_length"],
                metric["memory_count"],
                metric["metadata"],
            ),
        )

        conn.commit()
        conn.close()

    def record_user_feedback(
        self,
        feedback_type: str,
        rating: int,
        comment: str = None,
        project_id: str = None,
        context_summary: str = None,
    ):
        """Record user feedback about context injection."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_feedback
            (timestamp, feedback_type, rating, comment, project_id, context_summary)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now().isoformat(),
                feedback_type,
                rating,
                comment,
                project_id,
                context_summary,
            ),
        )

        conn.commit()
        conn.close()

    def record_usage_pattern(
        self,
        action_type: str,
        project_id: str = None,
        context_used: bool = False,
        manual_trigger: bool = False,
        user_id: str = None,
        session_id: str = None,
    ):
        """Record usage patterns for analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO usage_patterns
            (timestamp, user_id, session_id, action_type, project_id,
             context_used, manual_trigger)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now().isoformat(),
                user_id,
                session_id,
                action_type,
                project_id,
                context_used,
                manual_trigger,
            ),
        )

        conn.commit()
        conn.close()

    def get_performance_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate a performance report for the last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get date range
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Overall metrics
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_events,
                AVG(duration_ms) as avg_duration,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_events,
                COUNT(DISTINCT project_id) as unique_projects
            FROM performance_metrics
            WHERE timestamp >= ?
        """,
            (start_date,),
        )

        overall_stats = cursor.fetchone()

        # Event type breakdown
        cursor.execute(
            """
            SELECT event_type, COUNT(*) as count, AVG(duration_ms) as avg_duration
            FROM performance_metrics
            WHERE timestamp >= ?
            GROUP BY event_type
        """,
            (start_date,),
        )

        event_breakdown = cursor.fetchall()

        # User feedback summary
        cursor.execute(
            """
            SELECT feedback_type, AVG(rating) as avg_rating, COUNT(*) as count
            FROM user_feedback
            WHERE timestamp >= ?
            GROUP BY feedback_type
        """,
            (start_date,),
        )

        feedback_summary = cursor.fetchall()

        # Usage patterns
        cursor.execute(
            """
            SELECT action_type, COUNT(*) as count,
                   SUM(CASE WHEN context_used THEN 1 ELSE 0 END) as context_used_count,
                   SUM(CASE WHEN manual_trigger THEN 1 ELSE 0 END) as manual_trigger_count
            FROM usage_patterns
            WHERE timestamp >= ?
            GROUP BY action_type
        """,
            (start_date,),
        )

        usage_patterns = cursor.fetchall()

        conn.close()

        return {
            "period_days": days,
            "overall_stats": {
                "total_events": overall_stats[0],
                "avg_duration_ms": overall_stats[1],
                "success_rate": (
                    (overall_stats[2] / overall_stats[0]) * 100
                    if overall_stats[0] > 0
                    else 0
                ),
                "unique_projects": overall_stats[3],
            },
            "event_breakdown": [
                {"event_type": row[0], "count": row[1], "avg_duration_ms": row[2]}
                for row in event_breakdown
            ],
            "feedback_summary": [
                {"feedback_type": row[0], "avg_rating": row[1], "count": row[2]}
                for row in feedback_summary
            ],
            "usage_patterns": [
                {
                    "action_type": row[0],
                    "count": row[1],
                    "context_used_rate": (row[2] / row[1]) * 100 if row[1] > 0 else 0,
                    "manual_trigger_rate": (row[3] / row[1]) * 100 if row[1] > 0 else 0,
                }
                for row in usage_patterns
            ],
        }

    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on performance data."""
        report = self.get_performance_report(days=30)
        recommendations = []

        # Analyze success rate
        success_rate = report["overall_stats"]["success_rate"]
        if success_rate < 90:
            recommendations.append(
                "⚠️ Success rate below 90%. Consider improving error handling."
            )

        # Analyze average duration
        avg_duration = report["overall_stats"]["avg_duration_ms"]
        if avg_duration and avg_duration > 1000:
            recommendations.append(
                "🐌 Context injection taking >1s. Consider optimization."
            )

        # Analyze feedback
        feedback_ratings = [
            f["avg_rating"] for f in report["feedback_summary"] if f["avg_rating"]
        ]
        if feedback_ratings and sum(feedback_ratings) / len(feedback_ratings) < 4.0:
            recommendations.append(
                "⭐ User feedback below 4.0. Consider improving context quality."
            )

        # Analyze usage patterns
        for pattern in report["usage_patterns"]:
            if pattern["manual_trigger_rate"] > 50:
                recommendations.append(
                    "🎮 High manual trigger usage. Consider improving automatic injection."
                )

        if not recommendations:
            recommendations.append("✅ All metrics look good! System performing well.")

        return recommendations


class ContextInjectionMonitor:
    """Specialized monitor for context injection features."""

    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor

    def track_context_injection(
        self,
        project_id: str,
        context_length: int,
        duration_ms: float,
        success: bool,
        manual_trigger: bool = False,
    ):
        """Track context injection performance."""
        self.monitor.track_event(
            event_type="context_injection",
            project_id=project_id,
            duration_ms=duration_ms,
            success=success,
            context_length=context_length,
            metadata={"manual_trigger": manual_trigger},
        )

        self.monitor.record_usage_pattern(
            action_type="context_injection",
            project_id=project_id,
            context_used=True,
            manual_trigger=manual_trigger,
        )

    def track_memory_operation(
        self,
        operation_type: str,
        project_id: str,
        duration_ms: float,
        success: bool,
        memory_count: int = None,
    ):
        """Track memory operation performance."""
        self.monitor.track_event(
            event_type=f"memory_{operation_type}",
            project_id=project_id,
            duration_ms=duration_ms,
            success=success,
            memory_count=memory_count,
        )

    def record_context_feedback(
        self,
        rating: int,
        comment: str = None,
        project_id: str = None,
        context_summary: str = None,
    ):
        """Record user feedback about context quality."""
        self.monitor.record_user_feedback(
            feedback_type="context_quality",
            rating=rating,
            comment=comment,
            project_id=project_id,
            context_summary=context_summary,
        )


def main():
    """Test the performance monitoring system."""
    print("🧪 Testing Performance Monitoring System")
    print("=" * 50)

    monitor = PerformanceMonitor("test_performance.db")
    context_monitor = ContextInjectionMonitor(monitor)

    try:
        # Start monitoring
        monitor.start_monitoring()

        # Simulate some events
        print("\n📊 Simulating performance events...")

        # Context injection events
        context_monitor.track_context_injection(
            project_id="test-project",
            context_length=500,
            duration_ms=250,
            success=True,
            manual_trigger=False,
        )

        context_monitor.track_context_injection(
            project_id="test-project",
            context_length=300,
            duration_ms=150,
            success=True,
            manual_trigger=True,
        )

        # Memory operations
        context_monitor.track_memory_operation(
            operation_type="push",
            project_id="test-project",
            duration_ms=50,
            success=True,
            memory_count=1,
        )

        # User feedback
        context_monitor.record_context_feedback(
            rating=5,
            comment="Great context quality!",
            project_id="test-project",
            context_summary="User working on Python MCP server...",
        )

        # Wait for processing
        time.sleep(2)

        # Generate report
        print("\n📈 Performance Report:")
        print("-" * 40)
        report = monitor.get_performance_report(days=1)

        print(f"Total Events: {report['overall_stats']['total_events']}")
        print(f"Success Rate: {report['overall_stats']['success_rate']:.1f}%")
        print(f"Avg Duration: {report['overall_stats']['avg_duration_ms']:.1f}ms")

        print("\n📊 Event Breakdown:")
        for event in report["event_breakdown"]:
            print(
                f"• {event['event_type']}: {event['count']} events, {event['avg_duration_ms']:.1f}ms avg"
            )

        # Get recommendations
        print("\n💡 Recommendations:")
        recommendations = monitor.get_recommendations()
        for rec in recommendations:
            print(f"• {rec}")

        print("\n✅ Performance monitoring test completed!")

    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    main()
