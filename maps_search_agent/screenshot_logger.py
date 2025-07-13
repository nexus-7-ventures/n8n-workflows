#!/usr/bin/env python3
"""
Screenshot Logger for Maps Search Evaluation
Captures screenshots before/after each task with proper file management.
"""

import time
import os
import logging
from pathlib import Path
from datetime import datetime
import pyautogui
from PIL import Image
from typing import Dict, List, Optional, Any, Tuple


class ScreenshotLogger:
    """Screenshot logger for Maps Search Evaluation tasks"""
    
    def __init__(self, screenshots_dir: str = "screenshots"):
        self.logger = logging.getLogger(__name__)
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.enabled = True
        self.screenshot_count = 0
        self.screenshot_history = []
        self.logger.info(f"Screenshot logger initialized: {self.screenshots_dir}")
    
    def capture(self, task_type: str, task_id: str = None) -> Optional[str]:
        """Capture screenshot and save to file"""
        if not self.enabled:
            return None
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if task_id:
                filename = f"{task_type}_{task_id}_{timestamp}.png"
            else:
                filename = f"{task_type}_{timestamp}.png"
            
            filepath = self.screenshots_dir / filename
            
            # Capture screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            # Update tracking
            self.screenshot_count += 1
            self.screenshot_history.append({
                'timestamp': time.time(),
                'filename': filename,
                'task_type': task_type,
                'task_id': task_id,
                'file_size': filepath.stat().st_size
            })
            
            self.logger.info(f"Screenshot captured: {filename}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def get_screenshot_statistics(self) -> Dict[str, Any]:
        """Get screenshot statistics"""
        if not self.screenshot_history:
            return {
                'total_screenshots': 0,
                'total_size_mb': 0,
                'average_size_kb': 0,
                'task_type_distribution': {}
            }
        
        total_size = sum(s['file_size'] for s in self.screenshot_history)
        task_type_counts = {}
        
        for screenshot in self.screenshot_history:
            task_type = screenshot['task_type']
            task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1
        
        return {
            'total_screenshots': len(self.screenshot_history),
            'total_size_mb': total_size / (1024 * 1024),
            'average_size_kb': (total_size / len(self.screenshot_history)) / 1024,
            'task_type_distribution': task_type_counts
        }
    
    def enable(self):
        """Enable screenshot capture"""
        self.enabled = True
        self.logger.info("Screenshot capture enabled")
    
    def disable(self):
        """Disable screenshot capture"""
        self.enabled = False
        self.logger.info("Screenshot capture disabled")
    
    def close(self):
        """Close screenshot logger"""
        self.logger.info("Screenshot logger closed")
