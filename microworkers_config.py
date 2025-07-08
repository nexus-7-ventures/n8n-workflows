import os
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class MicroworkersConfig:
    """Configuration settings for Microworkers automation system"""
    
    # Base URLs and endpoints
    MICROWORKERS_BASE_URL = "https://microworkers.com"
    LOGIN_URL = f"{MICROWORKERS_BASE_URL}/sign_in"
    DASHBOARD_URL = f"{MICROWORKERS_BASE_URL}/dashboard"
    TASKS_URL = f"{MICROWORKERS_BASE_URL}/tasks"
    
    # Task filtering settings
    TASK_FILTERS = {
        "categories": ["click_search", "search_click", "web_search"],
        "min_payout": 0.10,  # Minimum $0.10 per task
        "max_time_minutes": 15,  # Maximum 15 minutes per task
        "desktop_only": True,
        "exclude_mobile": True,
        "exclude_video": True,
        "exclude_recording": True
    }
    
    # Timing and behavior settings
    TIMING_CONFIG = {
        "tasks_per_hour": {"min": 10, "max": 12},
        "between_tasks_delay": {"min": 7, "max": 12},  # seconds
        "page_load_wait": {"min": 2, "max": 4},
        "click_delay": {"min": 1, "max": 2},
        "scroll_delay": {"min": 0.5, "max": 1.5}
    }
    
    # Human-like behavior parameters
    MOUSE_CONFIG = {
        "movement_speed": {"min": 0.8, "max": 1.5},  # pixels per ms
        "curve_intensity": {"min": 0.3, "max": 0.7},  # how curved the path is
        "overshoot_probability": 0.15,  # chance of overshooting target
        "overshoot_distance": {"min": 5, "max": 15},  # pixels
        "jitter_amount": {"min": 1, "max": 3},  # random pixel variance
        "pause_probability": 0.25  # chance of mid-movement pause
    }
    
    # Screenshot and logging settings
    SCREENSHOT_CONFIG = {
        "save_directory": "./mw_screenshots",
        "format": "PNG",
        "quality": 95,
        "include_timestamp": True,
        "auto_cleanup_days": 30
    }
    
    # Browser settings
    BROWSER_CONFIG = {
        "default_browser": "chrome",
        "window_size": {"width": 1366, "height": 768},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "disable_images": False,
        "disable_javascript": False,
        "headless": False  # Always visible for human-like behavior
    }
    
    # Training mode settings
    TRAINING_CONFIG = {
        "record_mouse_patterns": True,
        "save_click_targets": True,
        "learn_page_layouts": True,
        "training_session_timeout": 300,  # 5 minutes
        "min_training_samples": 5
    }
    
    # Error handling and retry settings
    ERROR_CONFIG = {
        "max_retries": 3,
        "retry_delay": {"min": 5, "max": 10},
        "timeout_seconds": 30,
        "max_consecutive_failures": 5
    }

class ConfigManager:
    """Manages configuration loading and saving"""
    
    def __init__(self, config_path: str = "./config/microworkers_config.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = MicroworkersConfig()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file if it exists"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    # Update config object with loaded data
                    for key, value in config_data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            config_dict = {
                attr: getattr(self.config, attr) 
                for attr in dir(self.config) 
                if not attr.startswith('_')
            }
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def update_setting(self, section: str, key: str, value) -> None:
        """Update a specific configuration setting"""
        if hasattr(self.config, section):
            section_dict = getattr(self.config, section)
            if isinstance(section_dict, dict) and key in section_dict:
                section_dict[key] = value
                self.save_config()
    
    def get_setting(self, section: str, key: str = None):
        """Get a configuration setting"""
        if hasattr(self.config, section):
            section_value = getattr(self.config, section)
            if key is None:
                return section_value
            elif isinstance(section_value, dict) and key in section_value:
                return section_value[key]
        return None

# Global configuration instance
config_manager = ConfigManager()
config = config_manager.config