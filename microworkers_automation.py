import time
import random
import re
import json
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List, Optional, Tuple
import logging

from human_automation import HumanBrowserAutomation, HumanTyping
from microworkers_config import config

logger = logging.getLogger(__name__)

class TaskFilter:
    """Filters tasks based on requirements"""
    
    @staticmethod
    def is_click_search_task(task_title: str, task_description: str) -> bool:
        """Check if task is a Click + Search type"""
        click_search_keywords = [
            "click", "search", "find", "visit", "browse", "navigate",
            "go to", "look for", "check", "view", "open"
        ]
        
        exclude_keywords = [
            "video", "record", "upload", "mobile", "app", "download",
            "install", "phone", "android", "ios", "iphone"
        ]
        
        text = f"{task_title} {task_description}".lower()
        
        # Must contain click/search keywords
        has_required = any(keyword in text for keyword in click_search_keywords)
        
        # Must not contain excluded keywords
        has_excluded = any(keyword in text for keyword in exclude_keywords)
        
        return has_required and not has_excluded
    
    @staticmethod
    def is_desktop_compatible(task_description: str) -> bool:
        """Check if task is desktop compatible"""
        mobile_indicators = [
            "mobile", "phone", "android", "ios", "iphone", "app store",
            "play store", "smartphone", "tablet", "ipad"
        ]
        
        text = task_description.lower()
        return not any(indicator in text for indicator in mobile_indicators)
    
    @staticmethod
    def check_payout(payout_str: str) -> bool:
        """Check if payout meets minimum requirements"""
        try:
            # Extract numeric value from payout string
            payout_match = re.search(r'\$?([\d.]+)', payout_str)
            if payout_match:
                payout = float(payout_match.group(1))
                return payout >= config.TASK_FILTERS["min_payout"]
        except (ValueError, AttributeError):
            pass
        return False
    
    @staticmethod
    def check_time_requirement(time_str: str) -> bool:
        """Check if time requirement is acceptable"""
        try:
            # Extract minutes from time string
            time_match = re.search(r'(\d+)\s*min', time_str.lower())
            if time_match:
                minutes = int(time_match.group(1))
                return minutes <= config.TASK_FILTERS["max_time_minutes"]
        except (ValueError, AttributeError):
            pass
        return True  # Default to true if time not specified

class MicroworkersTask:
    """Represents a Microworkers task"""
    
    def __init__(self, element, automation: HumanBrowserAutomation):
        self.element = element
        self.automation = automation
        self.title = ""
        self.description = ""
        self.payout = ""
        self.time_required = ""
        self.task_id = ""
        self.is_valid = False
        self.parse_task_details()
    
    def parse_task_details(self) -> None:
        """Parse task details from the element"""
        try:
            # Extract task title
            title_element = self.element.find_element(By.CLASS_NAME, "task-title")
            self.title = title_element.text.strip()
            
            # Extract task description
            desc_element = self.element.find_element(By.CLASS_NAME, "task-description")
            self.description = desc_element.text.strip()
            
            # Extract payout
            payout_element = self.element.find_element(By.CLASS_NAME, "task-payout")
            self.payout = payout_element.text.strip()
            
            # Extract time requirement
            time_element = self.element.find_element(By.CLASS_NAME, "task-time")
            self.time_required = time_element.text.strip()
            
            # Extract task ID
            task_link = self.element.find_element(By.TAG_NAME, "a")
            task_url = task_link.get_attribute("href")
            task_id_match = re.search(r'/tasks/(\d+)', task_url)
            if task_id_match:
                self.task_id = task_id_match.group(1)
            
            self.validate_task()
            
        except NoSuchElementException as e:
            logger.warning(f"Failed to parse task details: {e}")
    
    def validate_task(self) -> None:
        """Validate if task meets all requirements"""
        self.is_valid = (
            TaskFilter.is_click_search_task(self.title, self.description) and
            TaskFilter.is_desktop_compatible(self.description) and
            TaskFilter.check_payout(self.payout) and
            TaskFilter.check_time_requirement(self.time_required)
        )
        
        logger.info(f"Task {self.task_id} validation: {self.is_valid}")
    
    def accept_task(self) -> bool:
        """Accept the task with human-like behavior"""
        try:
            # Find accept button
            accept_button = self.element.find_element(By.CLASS_NAME, "accept-task-btn")
            
            # Scroll to task if needed
            self.automation.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", 
                self.element
            )
            time.sleep(random.uniform(1, 2))
            
            # Click accept button
            success = self.automation.click_delayed(accept_button)
            
            if success:
                logger.info(f"Task {self.task_id} accepted successfully")
                # Take screenshot for confirmation
                self.automation.take_screenshot(f"task_accepted_{self.task_id}")
                return True
            else:
                logger.error(f"Failed to accept task {self.task_id}")
                return False
                
        except NoSuchElementException:
            logger.error(f"Accept button not found for task {self.task_id}")
            return False

class MicroworkersAutomation:
    """Main automation class for Microworkers"""
    
    def __init__(self):
        self.automation = HumanBrowserAutomation()
        self.is_logged_in = False
        self.session_stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "session_start": datetime.now(),
            "earnings": 0.0
        }
        self.consecutive_failures = 0
    
    def login(self, username: str, password: str) -> bool:
        """Login to Microworkers with human-like behavior"""
        try:
            # Navigate to login page
            logger.info("Navigating to Microworkers login page...")
            if not self.automation.navigate_to_url(config.LOGIN_URL):
                return False
            
            # Find login form elements
            username_field = self.automation.find_element_safely(By.ID, "user_email")
            password_field = self.automation.find_element_safely(By.ID, "user_password")
            login_button = self.automation.find_element_safely(By.CSS_SELECTOR, "input[type='submit']")
            
            if not all([username_field, password_field, login_button]):
                logger.error("Login form elements not found")
                return False
            
            # Human-like typing
            logger.info("Entering login credentials...")
            HumanTyping.type_like_human(username_field, username)
            time.sleep(random.uniform(0.5, 1.0))
            HumanTyping.type_like_human(password_field, password)
            
            # Random pause before clicking login
            time.sleep(random.uniform(1, 3))
            
            # Click login button
            self.automation.click_delayed(login_button)
            
            # Wait for login redirect
            self.automation.wait_for_page_load()
            
            # Verify login success
            current_url = self.automation.driver.current_url
            if "dashboard" in current_url.lower():
                self.is_logged_in = True
                logger.info("Login successful!")
                self.automation.take_screenshot("login_success")
                return True
            else:
                logger.error("Login failed - not redirected to dashboard")
                self.automation.take_screenshot("login_failed")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def navigate_to_tasks(self) -> bool:
        """Navigate to tasks page"""
        if not self.is_logged_in:
            logger.error("Not logged in")
            return False
        
        try:
            # Navigate to tasks page
            logger.info("Navigating to tasks page...")
            if not self.automation.navigate_to_url(config.TASKS_URL):
                return False
            
            # Wait for tasks to load
            self.automation.wait_for_page_load()
            
            # Random scroll to simulate browsing
            self.automation.scroll_smoothly("down", random.randint(1, 3))
            time.sleep(random.uniform(2, 4))
            
            return True
            
        except Exception as e:
            logger.error(f"Navigation to tasks failed: {e}")
            return False
    
    def find_valid_tasks(self) -> List[MicroworkersTask]:
        """Find all valid Click + Search tasks"""
        try:
            # Find all task elements
            task_elements = self.automation.find_elements_safely(By.CLASS_NAME, "task-item")
            
            if not task_elements:
                logger.warning("No task elements found")
                return []
            
            logger.info(f"Found {len(task_elements)} task elements")
            
            # Parse and filter tasks
            valid_tasks = []
            for element in task_elements:
                task = MicroworkersTask(element, self.automation)
                if task.is_valid:
                    valid_tasks.append(task)
            
            # Sort by payout (highest first)
            valid_tasks.sort(key=lambda t: self.extract_payout_value(t.payout), reverse=True)
            
            logger.info(f"Found {len(valid_tasks)} valid Click + Search tasks")
            return valid_tasks
            
        except Exception as e:
            logger.error(f"Error finding tasks: {e}")
            return []
    
    def extract_payout_value(self, payout_str: str) -> float:
        """Extract numeric payout value for sorting"""
        try:
            payout_match = re.search(r'\$?([\d.]+)', payout_str)
            if payout_match:
                return float(payout_match.group(1))
        except (ValueError, AttributeError):
            pass
        return 0.0
    
    def execute_task(self, task: MicroworkersTask) -> bool:
        """Execute a Click + Search task"""
        try:
            logger.info(f"Executing task {task.task_id}: {task.title}")
            
            # Accept the task
            if not task.accept_task():
                return False
            
            # Wait for task page to load
            self.automation.wait_for_page_load()
            
            # Take screenshot of task instructions
            self.automation.take_screenshot(f"task_instructions_{task.task_id}")
            
            # Simulate reading instructions
            time.sleep(random.uniform(5, 10))
            self.automation.scroll_smoothly("down", 2)
            time.sleep(random.uniform(3, 6))
            
            # Look for task-specific elements
            self.perform_click_search_actions()
            
            # Complete task submission
            return self.submit_task_completion(task.task_id)
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return False
    
    def perform_click_search_actions(self) -> None:
        """Perform the actual click and search actions"""
        try:
            # Look for search boxes
            search_elements = self.automation.find_elements_safely(By.CSS_SELECTOR, "input[type='search'], input[placeholder*='search']")
            
            if search_elements:
                search_box = search_elements[0]
                # Perform search with human-like typing
                search_term = self.get_random_search_term()
                HumanTyping.type_like_human(search_box, search_term)
                
                # Submit search
                search_box.submit()
                self.automation.wait_for_page_load()
            
            # Look for clickable elements
            clickable_elements = self.automation.find_elements_safely(By.CSS_SELECTOR, "a, button, [onclick]")
            
            if clickable_elements:
                # Click a few random elements
                for _ in range(random.randint(2, 4)):
                    if clickable_elements:
                        element = random.choice(clickable_elements)
                        # Check if it's not a "Remove" button
                        element_text = element.text.lower()
                        if "remove" not in element_text:
                            self.automation.click_delayed(element)
                            self.automation.wait_for_page_load()
                            time.sleep(random.uniform(2, 5))
            
        except Exception as e:
            logger.warning(f"Action performance warning: {e}")
    
    def get_random_search_term(self) -> str:
        """Get a random search term for tasks"""
        search_terms = [
            "products", "services", "information", "reviews", "news",
            "business", "company", "website", "online", "shopping"
        ]
        return random.choice(search_terms)
    
    def submit_task_completion(self, task_id: str) -> bool:
        """Submit task as completed"""
        try:
            # Look for completion button
            completion_buttons = self.automation.find_elements_safely(
                By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit'], .complete-task, .submit-task"
            )
            
            if completion_buttons:
                # Take screenshot before submission
                self.automation.take_screenshot(f"before_submit_{task_id}")
                
                # Click submit button
                submit_button = completion_buttons[0]
                self.automation.click_delayed(submit_button)
                
                # Wait for confirmation
                self.automation.wait_for_page_load()
                time.sleep(random.uniform(2, 4))
                
                # Take screenshot after submission
                self.automation.take_screenshot(f"after_submit_{task_id}")
                
                logger.info(f"Task {task_id} submitted successfully")
                return True
            else:
                logger.warning(f"No submit button found for task {task_id}")
                return False
                
        except Exception as e:
            logger.error(f"Task submission failed: {e}")
            return False
    
    def run_automation_cycle(self) -> None:
        """Run one complete automation cycle"""
        try:
            # Navigate to tasks
            if not self.navigate_to_tasks():
                return
            
            # Find valid tasks
            valid_tasks = self.find_valid_tasks()
            
            if not valid_tasks:
                logger.info("No valid tasks found")
                return
            
            # Execute tasks (limit to prevent overload)
            max_tasks_per_cycle = 3
            tasks_to_execute = valid_tasks[:max_tasks_per_cycle]
            
            for task in tasks_to_execute:
                # Check if we should continue based on timing
                if self.should_continue_session():
                    success = self.execute_task(task)
                    
                    if success:
                        self.session_stats["tasks_completed"] += 1
                        self.consecutive_failures = 0
                        logger.info(f"Task completed successfully. Total: {self.session_stats['tasks_completed']}")
                    else:
                        self.session_stats["tasks_failed"] += 1
                        self.consecutive_failures += 1
                        logger.warning(f"Task failed. Consecutive failures: {self.consecutive_failures}")
                    
                    # Check failure threshold
                    if self.consecutive_failures >= config.ERROR_CONFIG["max_consecutive_failures"]:
                        logger.error("Too many consecutive failures. Stopping session.")
                        break
                    
                    # Random pause between tasks
                    self.automation.random_pause_between_tasks()
                else:
                    logger.info("Session time limit reached")
                    break
            
        except Exception as e:
            logger.error(f"Automation cycle error: {e}")
    
    def should_continue_session(self) -> bool:
        """Check if session should continue based on timing and limits"""
        session_duration = datetime.now() - self.session_stats["session_start"]
        max_session_hours = 8  # Maximum 8 hours per session
        
        # Check time limits
        if session_duration.total_seconds() > max_session_hours * 3600:
            return False
        
        # Check task rate (10-12 per hour)
        hours_elapsed = session_duration.total_seconds() / 3600
        if hours_elapsed > 0:
            tasks_per_hour = self.session_stats["tasks_completed"] / hours_elapsed
            max_rate = config.TIMING_CONFIG["tasks_per_hour"]["max"]
            
            if tasks_per_hour > max_rate:
                logger.info(f"Task rate too high: {tasks_per_hour:.1f}/hour. Slowing down.")
                time.sleep(300)  # 5 minute cooldown
        
        return True
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        session_duration = datetime.now() - self.session_stats["session_start"]
        
        return {
            **self.session_stats,
            "session_duration_minutes": session_duration.total_seconds() / 60,
            "success_rate": (
                self.session_stats["tasks_completed"] / 
                max(1, self.session_stats["tasks_completed"] + self.session_stats["tasks_failed"])
            ) * 100
        }
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.automation.quit_browser()
        logger.info("Automation cleanup completed")