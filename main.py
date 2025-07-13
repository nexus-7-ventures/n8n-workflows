#!/usr/bin/env python3
"""
Maps Search Evaluation Agent - Main Entry Point
Fully offline, screen-based AI agent for autonomous Maps Search Evaluation tasks.
"""

import sys
import time
import logging
from pathlib import Path
import signal
from typing import Dict, Any

from mouse_controller import MouseController
from keyboard_sim import KeyboardSimulator
from ocr_reader import OCRReader
from rating_engine import RatingEngine
from comment_generator import CommentGenerator
from throttler import TaskThrottler
from logger import TaskLogger
from qa_agent import QAAgent
from screenshot_logger import ScreenshotLogger


class MapsSearchAgent:
    """Main Maps Search Evaluation Agent"""
    
    def __init__(self):
        self.running = False
        self.setup_logging()
        self.load_guidelines()
        self.initialize_components()
        
    def setup_logging(self):
        """Setup main application logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agent.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_guidelines(self):
        """Load and validate guidelines.txt"""
        guidelines_path = Path("guidelines.txt")
        if not guidelines_path.exists():
            self.logger.error("guidelines.txt not found! Please add the file to the project directory.")
            sys.exit(1)
            
        try:
            with open(guidelines_path, 'r', encoding='utf-8') as f:
                self.guidelines_content = f.read()
            self.logger.info("Guidelines loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load guidelines.txt: {e}")
            sys.exit(1)
            
    def initialize_components(self):
        """Initialize all agent components"""
        try:
            self.mouse = MouseController()
            self.keyboard = KeyboardSimulator()
            self.ocr = OCRReader()
            self.rating_engine = RatingEngine(self.guidelines_content)
            self.comment_generator = CommentGenerator()
            self.throttler = TaskThrottler()
            self.task_logger = TaskLogger()
            self.qa_agent = QAAgent()
            self.screenshot_logger = ScreenshotLogger()
            
            self.logger.info("All components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            sys.exit(1)
            
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info("Shutdown signal received. Stopping agent...")
        self.running = False
        
    def perform_task(self) -> Dict[str, Any]:
        """Perform a single Maps Search Evaluation task"""
        task_start = time.time()
        
        # Take screenshot before task
        screenshot_before = self.screenshot_logger.capture("before_task")
        
        # Simulate human-like random movement before starting
        self.mouse.random_screen_movement()
        
        # Read current screen content
        screen_text = self.ocr.read_screen()
        
        # Extract query and map results
        query_info = self.ocr.extract_query_info(screen_text)
        map_results = self.ocr.extract_map_results(screen_text)
        
        # Apply rating logic
        rating_result = self.rating_engine.evaluate_results(query_info, map_results)
        
        # Generate appropriate comment
        comment = self.comment_generator.generate_comment(rating_result)
        
        # QA validation
        validation = self.qa_agent.validate_rating_comment(rating_result, comment)
        if not validation['valid']:
            self.logger.warning(f"QA validation failed: {validation['reason']}")
            # Retry with corrected logic
            rating_result = self.rating_engine.correct_rating(rating_result, validation)
            comment = self.comment_generator.generate_comment(rating_result)
        
        # Simulate mouse interaction to submit rating
        self.mouse.submit_rating(rating_result['rating'])
        
        # Type comment with human-like behavior
        if comment:
            self.keyboard.type_comment(comment)
        
        # More random behavior after task
        self.mouse.random_post_task_behavior()
        
        # Take screenshot after task
        screenshot_after = self.screenshot_logger.capture("after_task")
        
        # Log the completed task
        task_data = {
            'timestamp': time.time(),
            'query': query_info.get('query', 'Unknown'),
            'rating': rating_result['rating'],
            'demotion_reason': rating_result.get('demotion_reason', ''),
            'comment': comment,
            'screenshot_before': screenshot_before,
            'screenshot_after': screenshot_after,
            'duration': time.time() - task_start
        }
        
        self.task_logger.log_task(task_data)
        
        return task_data
        
    def run(self):
        """Main agent loop"""
        self.logger.info("Starting Maps Search Evaluation Agent...")
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        task_count = 0
        
        while self.running:
            try:
                # Check if we should perform a task (pacing control)
                if self.throttler.should_perform_task():
                    self.logger.info(f"Starting task #{task_count + 1}")
                    
                    task_result = self.perform_task()
                    task_count += 1
                    
                    self.logger.info(f"Task #{task_count} completed: {task_result['query']}")
                    
                    # Update throttler with task completion
                    self.throttler.task_completed()
                    
                else:
                    # Wait and perform idle behavior
                    self.mouse.idle_behavior()
                    time.sleep(5)  # Check again in 5 seconds
                    
            except KeyboardInterrupt:
                self.logger.info("User interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(10)  # Wait before retrying
                
        self.logger.info(f"Agent stopped. Completed {task_count} tasks.")


if __name__ == "__main__":
    print("Maps Search Evaluation Agent v1.0")
    print("=" * 50)
    
    agent = MapsSearchAgent()
    
    try:
        agent.run()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)