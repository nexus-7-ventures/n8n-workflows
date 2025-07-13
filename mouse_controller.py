#!/usr/bin/env python3
"""
Advanced Mouse Controller with Human-like Behavior Simulation
Includes anti-detection features and realistic movement patterns.
"""

import time
import random
import math
import pyautogui
import numpy as np
from typing import Tuple, List, Optional
import logging
from dataclasses import dataclass


@dataclass
class MouseProfile:
    """Human-like mouse behavior profile"""
    base_speed: float = 0.5
    jitter_factor: float = 0.1
    pause_probability: float = 0.3
    overshoot_probability: float = 0.2
    acceleration_factor: float = 1.2
    deceleration_factor: float = 0.8


class MouseController:
    """Advanced mouse controller with human-like behavior"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.profile = MouseProfile()
        self.screen_width, self.screen_height = pyautogui.size()
        self.last_position = pyautogui.position()
        
        # Disable pyautogui failsafe for autonomous operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1
        
        # Common UI zones for realistic behavior
        self.ui_zones = {
            'search_box': (self.screen_width // 2, 100),
            'map_center': (self.screen_width // 2, self.screen_height // 2),
            'rating_area': (self.screen_width - 300, self.screen_height - 200),
            'sidebar': (300, self.screen_height // 2),
            'top_bar': (self.screen_width // 2, 50),
        }
        
        self.logger.info("Mouse controller initialized")
    
    def _calculate_bezier_curve(self, start: Tuple[int, int], end: Tuple[int, int], 
                              control_points: int = 3) -> List[Tuple[int, int]]:
        """Generate smooth bezier curve path between two points"""
        points = []
        
        # Generate random control points for natural curve
        mid_x = (start[0] + end[0]) // 2
        mid_y = (start[1] + end[1]) // 2
        
        # Add some randomness to control points
        ctrl1_x = mid_x + random.randint(-100, 100)
        ctrl1_y = mid_y + random.randint(-50, 50)
        
        ctrl2_x = mid_x + random.randint(-100, 100)
        ctrl2_y = mid_y + random.randint(-50, 50)
        
        # Calculate bezier curve points
        for i in range(control_points):
            t = i / (control_points - 1)
            
            # Cubic bezier formula
            x = (1-t)**3 * start[0] + 3*(1-t)**2*t * ctrl1_x + 3*(1-t)*t**2 * ctrl2_x + t**3 * end[0]
            y = (1-t)**3 * start[1] + 3*(1-t)**2*t * ctrl1_y + 3*(1-t)*t**2 * ctrl2_y + t**3 * end[1]
            
            points.append((int(x), int(y)))
        
        return points
    
    def _add_jitter(self, x: int, y: int) -> Tuple[int, int]:
        """Add human-like jitter to coordinates"""
        jitter_x = random.randint(-int(self.profile.jitter_factor * 10), 
                                 int(self.profile.jitter_factor * 10))
        jitter_y = random.randint(-int(self.profile.jitter_factor * 10), 
                                 int(self.profile.jitter_factor * 10))
        
        return (x + jitter_x, y + jitter_y)
    
    def _human_like_move(self, target_x: int, target_y: int, duration: float = None):
        """Move mouse with human-like behavior"""
        current_x, current_y = pyautogui.position()
        
        # Calculate distance for speed adjustment
        distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
        
        if duration is None:
            # Base duration on distance with some randomness
            duration = (distance / 1000) * self.profile.base_speed + random.uniform(0.1, 0.3)
        
        # Generate smooth path
        path_points = self._calculate_bezier_curve((current_x, current_y), (target_x, target_y))
        
        # Move along the path
        for i, (x, y) in enumerate(path_points):
            # Add jitter
            jittered_x, jittered_y = self._add_jitter(x, y)
            
            # Move to point
            pyautogui.moveTo(jittered_x, jittered_y, duration=duration/len(path_points))
            
            # Random micro-pauses
            if random.random() < self.profile.pause_probability:
                time.sleep(random.uniform(0.01, 0.05))
        
        # Final position adjustment
        final_x, final_y = self._add_jitter(target_x, target_y)
        pyautogui.moveTo(final_x, final_y, duration=0.1)
        
        self.last_position = (final_x, final_y)
    
    def random_screen_movement(self):
        """Simulate random screen exploration behavior"""
        self.logger.info("Performing random screen movement")
        
        # Choose random UI zone to explore
        zone_name = random.choice(list(self.ui_zones.keys()))
        zone_x, zone_y = self.ui_zones[zone_name]
        
        # Add randomness to the zone coordinates
        target_x = zone_x + random.randint(-100, 100)
        target_y = zone_y + random.randint(-50, 50)
        
        # Ensure coordinates are within screen bounds
        target_x = max(50, min(self.screen_width - 50, target_x))
        target_y = max(50, min(self.screen_height - 50, target_y))
        
        # Move to random position
        self._human_like_move(target_x, target_y)
        
        # Random pause
        time.sleep(random.uniform(0.5, 2.0))
        
        # Sometimes scroll around
        if random.random() < 0.6:
            self._random_scroll()
    
    def _random_scroll(self):
        """Perform random scrolling behavior"""
        scroll_actions = random.randint(1, 3)
        
        for _ in range(scroll_actions):
            # Random scroll direction and amount
            scroll_direction = random.choice([-1, 1])
            scroll_amount = random.randint(1, 5)
            
            pyautogui.scroll(scroll_direction * scroll_amount)
            time.sleep(random.uniform(0.2, 0.8))
    
    def idle_behavior(self):
        """Simulate idle human behavior"""
        behaviors = [
            self._micro_movement,
            self._random_hover,
            self._brief_scroll,
            self._zone_exploration
        ]
        
        # Choose random behavior
        behavior = random.choice(behaviors)
        behavior()
    
    def _micro_movement(self):
        """Small random movements"""
        current_x, current_y = pyautogui.position()
        
        # Small random movement
        new_x = current_x + random.randint(-20, 20)
        new_y = current_y + random.randint(-20, 20)
        
        # Ensure within screen bounds
        new_x = max(0, min(self.screen_width, new_x))
        new_y = max(0, min(self.screen_height, new_y))
        
        self._human_like_move(new_x, new_y, duration=0.5)
    
    def _random_hover(self):
        """Hover over random screen areas"""
        hover_zones = ['map_center', 'sidebar', 'top_bar']
        zone = random.choice(hover_zones)
        
        if zone in self.ui_zones:
            zone_x, zone_y = self.ui_zones[zone]
            target_x = zone_x + random.randint(-50, 50)
            target_y = zone_y + random.randint(-25, 25)
            
            self._human_like_move(target_x, target_y)
            time.sleep(random.uniform(1.0, 3.0))
    
    def _brief_scroll(self):
        """Brief scrolling behavior"""
        scroll_count = random.randint(1, 2)
        for _ in range(scroll_count):
            direction = random.choice([-1, 1])
            pyautogui.scroll(direction * random.randint(1, 3))
            time.sleep(random.uniform(0.3, 0.7))
    
    def _zone_exploration(self):
        """Explore different UI zones"""
        zones = random.sample(list(self.ui_zones.keys()), 2)
        
        for zone in zones:
            zone_x, zone_y = self.ui_zones[zone]
            target_x = zone_x + random.randint(-30, 30)
            target_y = zone_y + random.randint(-20, 20)
            
            self._human_like_move(target_x, target_y)
            time.sleep(random.uniform(0.5, 1.5))
    
    def submit_rating(self, rating: str):
        """Submit rating with human-like interaction"""
        self.logger.info(f"Submitting rating: {rating}")
        
        # Move to rating area
        rating_x, rating_y = self.ui_zones['rating_area']
        self._human_like_move(rating_x, rating_y)
        
        # Pause before clicking
        time.sleep(random.uniform(0.3, 0.8))
        
        # Click rating button (simulated)
        pyautogui.click()
        
        # Brief pause after click
        time.sleep(random.uniform(0.2, 0.5))
        
    def random_post_task_behavior(self):
        """Random behavior after completing a task"""
        self.logger.info("Performing post-task behavior")
        
        behaviors = [
            self._look_around_map,
            self._check_other_results,
            self._brief_pause,
            self._scroll_exploration
        ]
        
        # Execute 1-2 random behaviors
        selected_behaviors = random.sample(behaviors, random.randint(1, 2))
        for behavior in selected_behaviors:
            behavior()
    
    def _look_around_map(self):
        """Look around the map area"""
        map_x, map_y = self.ui_zones['map_center']
        
        # Visit several points around the map
        for _ in range(random.randint(2, 4)):
            offset_x = random.randint(-200, 200)
            offset_y = random.randint(-150, 150)
            
            target_x = map_x + offset_x
            target_y = map_y + offset_y
            
            self._human_like_move(target_x, target_y)
            time.sleep(random.uniform(0.5, 1.2))
    
    def _check_other_results(self):
        """Check other search results"""
        sidebar_x, sidebar_y = self.ui_zones['sidebar']
        
        # Scroll through results
        self._human_like_move(sidebar_x, sidebar_y)
        time.sleep(random.uniform(0.3, 0.6))
        
        # Simulate checking multiple results
        for _ in range(random.randint(2, 5)):
            pyautogui.scroll(-1)
            time.sleep(random.uniform(0.4, 0.8))
    
    def _brief_pause(self):
        """Brief thinking pause"""
        time.sleep(random.uniform(1.0, 3.0))
    
    def _scroll_exploration(self):
        """Explore by scrolling"""
        scroll_actions = random.randint(3, 6)
        
        for _ in range(scroll_actions):
            direction = random.choice([-1, 1])
            amount = random.randint(1, 3)
            
            pyautogui.scroll(direction * amount)
            time.sleep(random.uniform(0.3, 0.7))
    
    def simulate_window_interaction(self):
        """Simulate window switching or focus changes"""
        self.logger.info("Simulating window interaction")
        
        # Simulate Alt+Tab or similar
        current_pos = pyautogui.position()
        
        # Move away briefly
        self._human_like_move(
            random.randint(100, self.screen_width - 100),
            random.randint(100, self.screen_height - 100)
        )
        
        # Pause (simulating focus loss)
        time.sleep(random.uniform(2.0, 5.0))
        
        # Return to original area
        self._human_like_move(current_pos[0], current_pos[1])
        
    def emergency_stop(self):
        """Emergency stop for the mouse controller"""
        self.logger.warning("Emergency stop activated")
        pyautogui.FAILSAFE = True
        
    def get_current_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()
    
    def is_position_valid(self, x: int, y: int) -> bool:
        """Check if position is within screen bounds"""
        return 0 <= x <= self.screen_width and 0 <= y <= self.screen_height