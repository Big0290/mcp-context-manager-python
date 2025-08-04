"""
Calendar plugin for the MCP Memory Server.
This plugin can extract calendar-related information from memories.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List
from mcp_memory_server.models.memory import Memory
from .base import BasePlugin


class CalendarPlugin(BasePlugin):
    """Plugin for extracting and processing calendar-related memories."""
    
    def __init__(self):
        super().__init__(
            name="calendar_plugin",
            description="Extracts calendar events and deadlines from memories"
        )
        self.date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',      # YYYY-MM-DD
            r'\b(today|tomorrow|next week|next month)\b',  # Relative dates
            r'\b(deadline|due date|meeting|appointment)\b'  # Event keywords
        ]
    
    def process_memory(self, memory: Memory) -> Memory:
        """Extract calendar information from memory content."""
        if not self.enabled:
            return memory
        
        # Extract dates and events
        dates = self._extract_dates(memory.content)
        events = self._extract_events(memory.content)
        
        if dates or events:
            # Add calendar metadata
            calendar_data = {
                "dates": dates,
                "events": events,
                "processed_by": self.name
            }
            
            # Update memory metadata
            if not memory.custom_metadata:
                memory.custom_metadata = {}
            
            memory.custom_metadata["calendar"] = calendar_data
            
            # Add calendar tags
            if "calendar" not in memory.tags:
                memory.tags.append("calendar")
        
        return memory
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from content."""
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        return list(set(dates))
    
    def _extract_events(self, content: str) -> List[str]:
        """Extract event keywords from content."""
        event_keywords = [
            "deadline", "due date", "meeting", "appointment", 
            "call", "conference", "presentation", "review"
        ]
        
        events = []
        for keyword in event_keywords:
            if keyword.lower() in content.lower():
                events.append(keyword)
        
        return events
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        info = super().get_plugin_info()
        info.update({
            "date_patterns": len(self.date_patterns),
            "event_keywords": 8  # Number of event keywords
        })
        return info 