import time
from collections import defaultdict
from typing import Set

class DeduplicationService:
    def __init__(self, window_seconds: float = 2.0):
        self.window_seconds = window_seconds
        self.action_timestamps = defaultdict(float)
        self.recent_actions: Set[str] = set()
    
    def should_log_action(self, action_type: str, user_id: int, unique_key: str = None) -> bool:
        """
        Check if an action should be logged based on deduplication rules
        """
        if unique_key:
            cache_key = f"{action_type}_{user_id}_{unique_key}"
        else:
            cache_key = f"{action_type}_{user_id}"
        
        current_time = time.time()
        
        # Check if this action was logged recently
        if current_time - self.action_timestamps.get(cache_key, 0) <= self.window_seconds:
            return False
        
        # Update the timestamp
        self.action_timestamps[cache_key] = current_time
        return True
    
    def clear_old_entries(self):
        """Clean up old cache entries (optional)"""
        current_time = time.time()
        old_keys = [
            key for key, timestamp in self.action_timestamps.items()
            if current_time - timestamp > 3600  # 1 hour
        ]
        for key in old_keys:
            del self.action_timestamps[key]

# Global instance
dedupe_service = DeduplicationService(window_seconds=2.0)