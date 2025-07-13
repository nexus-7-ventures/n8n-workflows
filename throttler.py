#!/usr/bin/env python3
"""
Task Throttler for Maps Search Evaluation
Enforces 24±3 tasks per hour with randomized pauses and longer breaks.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import deque


@dataclass
class TaskRecord:
    """Record of a completed task"""
    timestamp: float
    duration: float
    task_id: str = ""


class TaskThrottler:
    """Controls task pacing to maintain 24±3 tasks per hour"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.target_tasks_per_hour = 24
        self.variance_range = 3  # ±3 tasks
        self.min_tasks_per_hour = self.target_tasks_per_hour - self.variance_range
        self.max_tasks_per_hour = self.target_tasks_per_hour + self.variance_range
        
        # Timing calculations
        self.base_interval = 3600 / self.target_tasks_per_hour  # 150 seconds
        self.min_interval = 3600 / self.max_tasks_per_hour  # ~133 seconds
        self.max_interval = 3600 / self.min_tasks_per_hour  # ~171 seconds
        
        # Task tracking
        self.task_history: deque = deque(maxlen=100)
        self.session_start_time = time.time()
        self.last_task_time = 0
        self.tasks_completed = 0
        
        # Break management
        self.tasks_since_last_break = 0
        self.break_threshold = random.randint(10, 12)  # Break after 10-12 tasks
        self.last_break_time = time.time()
        
        # Current hour tracking
        self.current_hour_start = time.time()
        self.current_hour_tasks = 0
        
        self.logger.info(f"Task throttler initialized: {self.min_tasks_per_hour}-{self.max_tasks_per_hour} tasks/hour")
    
    def should_perform_task(self) -> bool:
        """Determine if a task should be performed now"""
        current_time = time.time()
        
        # Check if we need a break
        if self._should_take_break(current_time):
            self.logger.info("Taking scheduled break")
            return False
        
        # Check if we've reached hourly limit
        if self._reached_hourly_limit(current_time):
            self.logger.info("Hourly task limit reached, waiting")
            return False
        
        # Check if enough time has passed since last task
        if self._should_wait_longer(current_time):
            return False
        
        return True
    
    def _should_take_break(self, current_time: float) -> bool:
        """Check if it's time for a break"""
        # Check if we've done enough tasks for a break
        if self.tasks_since_last_break >= self.break_threshold:
            return True
        
        # Check if it's been too long since last break (max 2 hours)
        if current_time - self.last_break_time > 7200:  # 2 hours
            return True
        
        return False
    
    def _reached_hourly_limit(self, current_time: float) -> bool:
        """Check if we've reached the hourly task limit"""
        # Reset hour counter if hour has passed
        if current_time - self.current_hour_start >= 3600:
            self.current_hour_start = current_time
            self.current_hour_tasks = 0
            self.logger.info("New hour started, resetting task counter")
        
        # Check if we've exceeded max tasks for this hour
        return self.current_hour_tasks >= self.max_tasks_per_hour
    
    def _should_wait_longer(self, current_time: float) -> bool:
        """Check if we should wait longer before next task"""
        if self.last_task_time == 0:
            return False
        
        time_since_last = current_time - self.last_task_time
        required_interval = self._calculate_next_interval()
        
        return time_since_last < required_interval
    
    def _calculate_next_interval(self) -> float:
        """Calculate the interval until the next task"""
        # Base interval with randomization
        base_interval = random.uniform(self.min_interval, self.max_interval)
        
        # Adjust based on recent task rate
        recent_rate = self._get_recent_task_rate()
        if recent_rate > self.max_tasks_per_hour:
            # Slow down if going too fast
            base_interval *= 1.2
        elif recent_rate < self.min_tasks_per_hour:
            # Speed up if going too slow
            base_interval *= 0.8
        
        # Add natural variation
        variation = random.uniform(-30, 30)  # ±30 seconds
        final_interval = base_interval + variation
        
        # Ensure reasonable bounds
        return max(60, min(300, final_interval))  # 1-5 minutes
    
    def _get_recent_task_rate(self) -> float:
        """Get task rate for the last hour"""
        if len(self.task_history) < 2:
            return self.target_tasks_per_hour
        
        current_time = time.time()
        recent_tasks = [task for task in self.task_history 
                       if current_time - task.timestamp <= 3600]
        
        if not recent_tasks:
            return 0
        
        return len(recent_tasks)
    
    def task_completed(self, task_id: str = "", duration: float = 0):
        """Record a completed task"""
        current_time = time.time()
        
        # Record the task
        task_record = TaskRecord(
            timestamp=current_time,
            duration=duration,
            task_id=task_id
        )
        self.task_history.append(task_record)
        
        # Update counters
        self.tasks_completed += 1
        self.current_hour_tasks += 1
        self.tasks_since_last_break += 1
        self.last_task_time = current_time
        
        self.logger.info(f"Task completed: {self.tasks_completed} total, "
                        f"{self.current_hour_tasks} this hour")
        
        # Check if we need to take a break after this task
        if self.tasks_since_last_break >= self.break_threshold:
            self._schedule_break()
    
    def _schedule_break(self):
        """Schedule a break after completing tasks"""
        break_duration = random.uniform(300, 600)  # 5-10 minutes
        self.logger.info(f"Scheduling break for {break_duration:.1f} seconds")
        
        # Reset break counters
        self.tasks_since_last_break = 0
        self.last_break_time = time.time()
        self.break_threshold = random.randint(10, 12)  # Next break after 10-12 tasks
        
        # Actually take the break
        time.sleep(break_duration)
        self.logger.info("Break completed")
    
    def get_next_task_delay(self) -> float:
        """Get the delay until the next task should be performed"""
        if self.should_perform_task():
            return 0
        
        current_time = time.time()
        
        # If we need a break, return break duration
        if self._should_take_break(current_time):
            return random.uniform(300, 600)
        
        # If we've reached hourly limit, wait until next hour
        if self._reached_hourly_limit(current_time):
            time_until_next_hour = 3600 - (current_time - self.current_hour_start)
            return time_until_next_hour
        
        # Calculate time until next task
        if self.last_task_time > 0:
            time_since_last = current_time - self.last_task_time
            required_interval = self._calculate_next_interval()
            return max(0, required_interval - time_since_last)
        
        return 0
    
    def get_throttling_status(self) -> Dict[str, Any]:
        """Get current throttling status"""
        current_time = time.time()
        
        return {
            'tasks_completed': self.tasks_completed,
            'current_hour_tasks': self.current_hour_tasks,
            'tasks_since_break': self.tasks_since_last_break,
            'recent_task_rate': self._get_recent_task_rate(),
            'next_task_delay': self.get_next_task_delay(),
            'time_until_break': self.break_threshold - self.tasks_since_last_break,
            'session_duration': current_time - self.session_start_time,
            'last_task_time': self.last_task_time,
            'target_range': f"{self.min_tasks_per_hour}-{self.max_tasks_per_hour}"
        }
    
    def adjust_pacing(self, target_tasks_per_hour: int):
        """Adjust the target pacing"""
        self.target_tasks_per_hour = target_tasks_per_hour
        self.min_tasks_per_hour = target_tasks_per_hour - self.variance_range
        self.max_tasks_per_hour = target_tasks_per_hour + self.variance_range
        
        # Recalculate intervals
        self.base_interval = 3600 / self.target_tasks_per_hour
        self.min_interval = 3600 / self.max_tasks_per_hour
        self.max_interval = 3600 / self.min_tasks_per_hour
        
        self.logger.info(f"Pacing adjusted to {self.min_tasks_per_hour}-{self.max_tasks_per_hour} tasks/hour")
    
    def force_break(self, duration: float = None):
        """Force a break for specified duration"""
        if duration is None:
            duration = random.uniform(300, 600)
        
        self.logger.info(f"Forcing break for {duration:.1f} seconds")
        
        self.tasks_since_last_break = 0
        self.last_break_time = time.time()
        self.break_threshold = random.randint(10, 12)
        
        time.sleep(duration)
        self.logger.info("Forced break completed")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        current_time = time.time()
        session_duration = current_time - self.session_start_time
        
        # Calculate average task rate
        if session_duration > 0:
            avg_tasks_per_hour = (self.tasks_completed / session_duration) * 3600
        else:
            avg_tasks_per_hour = 0
        
        # Calculate recent performance
        recent_tasks = [task for task in self.task_history 
                       if current_time - task.timestamp <= 3600]
        recent_rate = len(recent_tasks)
        
        # Calculate task intervals
        intervals = []
        for i in range(1, len(self.task_history)):
            interval = self.task_history[i].timestamp - self.task_history[i-1].timestamp
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        return {
            'session_duration_hours': session_duration / 3600,
            'total_tasks': self.tasks_completed,
            'average_tasks_per_hour': avg_tasks_per_hour,
            'recent_tasks_per_hour': recent_rate,
            'target_range': f"{self.min_tasks_per_hour}-{self.max_tasks_per_hour}",
            'average_interval_seconds': avg_interval,
            'target_interval_seconds': self.base_interval,
            'on_pace': self.min_tasks_per_hour <= avg_tasks_per_hour <= self.max_tasks_per_hour
        }
    
    def reset_session(self):
        """Reset session statistics"""
        self.task_history.clear()
        self.session_start_time = time.time()
        self.last_task_time = 0
        self.tasks_completed = 0
        self.tasks_since_last_break = 0
        self.last_break_time = time.time()
        self.current_hour_start = time.time()
        self.current_hour_tasks = 0
        
        self.logger.info("Session reset")
    
    def simulate_natural_delay(self):
        """Add natural delay between actions"""
        # Short random pause to simulate human thinking
        delay = random.uniform(1, 5)
        time.sleep(delay)
    
    def get_optimal_work_schedule(self) -> Dict[str, Any]:
        """Get optimal work schedule for the day"""
        # Calculate breaks and work periods
        tasks_per_break_cycle = (self.break_threshold + 1) // 2
        break_cycles_per_hour = 60 / (tasks_per_break_cycle * 2.5)  # Rough estimate
        
        return {
            'recommended_work_hours': 8,
            'total_daily_tasks': self.target_tasks_per_hour * 8,
            'break_frequency_minutes': 60 / break_cycles_per_hour,
            'break_duration_minutes': 7.5,  # Average break time
            'tasks_per_break_cycle': tasks_per_break_cycle,
            'hourly_distribution': {
                'min_tasks': self.min_tasks_per_hour,
                'target_tasks': self.target_tasks_per_hour,
                'max_tasks': self.max_tasks_per_hour
            }
        }
    
    def emergency_throttle(self, factor: float = 2.0):
        """Emergency throttling to slow down significantly"""
        original_min = self.min_tasks_per_hour
        original_max = self.max_tasks_per_hour
        
        self.min_tasks_per_hour = int(self.min_tasks_per_hour / factor)
        self.max_tasks_per_hour = int(self.max_tasks_per_hour / factor)
        
        self.logger.warning(f"Emergency throttling activated: "
                           f"{original_min}-{original_max} -> "
                           f"{self.min_tasks_per_hour}-{self.max_tasks_per_hour} tasks/hour")
        
        # Recalculate intervals
        self.min_interval = 3600 / self.max_tasks_per_hour
        self.max_interval = 3600 / self.min_tasks_per_hour