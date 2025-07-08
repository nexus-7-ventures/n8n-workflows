import time
import random
import math
import numpy as np
import pyautogui
import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image, ImageDraw
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Optional, Dict
import logging

from microworkers_config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HumanMouseMovement:
    """Generates human-like mouse movements with curves, jitter, and overshoots"""
    
    @staticmethod
    def bezier_curve(start: Tuple[int, int], end: Tuple[int, int], 
                    control_points: int = 3) -> List[Tuple[int, int]]:
        """Generate a Bezier curve path between two points"""
        def bezier_point(t: float, points: List[Tuple[int, int]]) -> Tuple[int, int]:
            n = len(points) - 1
            x = sum(math.comb(n, i) * (1-t)**(n-i) * t**i * points[i][0] for i in range(n+1))
            y = sum(math.comb(n, i) * (1-t)**(n-i) * t**i * points[i][1] for i in range(n+1))
            return (int(x), int(y))
        
        # Create control points for natural curve
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Add randomized control points
        curve_intensity = random.uniform(*config.MOUSE_CONFIG["curve_intensity"])
        control_offset = distance * curve_intensity
        
        control_x = start[0] + dx/2 + random.randint(-int(control_offset), int(control_offset))
        control_y = start[1] + dy/2 + random.randint(-int(control_offset), int(control_offset))
        
        points = [start, (control_x, control_y), end]
        
        # Generate curve points
        num_points = max(10, int(distance / 5))
        path = []
        for i in range(num_points + 1):
            t = i / num_points
            path.append(bezier_point(t, points))
        
        return path
    
    @staticmethod
    def add_jitter(path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Add random jitter to path points"""
        jitter_amount = config.MOUSE_CONFIG["jitter_amount"]
        jittered_path = []
        
        for x, y in path:
            jitter_x = random.randint(-jitter_amount["max"], jitter_amount["max"])
            jitter_y = random.randint(-jitter_amount["max"], jitter_amount["max"])
            jittered_path.append((x + jitter_x, y + jitter_y))
        
        return jittered_path
    
    @staticmethod
    def calculate_movement_speed(distance: float) -> float:
        """Calculate realistic movement speed based on distance"""
        base_speed = random.uniform(*config.MOUSE_CONFIG["movement_speed"])
        
        # Slower for longer distances (human fatigue simulation)
        if distance > 500:
            base_speed *= 0.8
        elif distance < 50:
            base_speed *= 1.2
        
        return base_speed

class HumanBrowserAutomation:
    """Main class for human-like browser automation"""
    
    def __init__(self):
        self.driver = None
        self.action_chains = None
        self.wait = None
        self.screenshot_count = 0
        self.setup_browser()
        
    def setup_browser(self) -> None:
        """Initialize browser with human-like settings"""
        chrome_options = Options()
        
        # Human-like browser settings
        chrome_options.add_argument(f"--user-agent={config.BROWSER_CONFIG['user_agent']}")
        chrome_options.add_argument(f"--window-size={config.BROWSER_CONFIG['window_size']['width']},{config.BROWSER_CONFIG['window_size']['height']}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Additional stealth options
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-service-autorun")
        chrome_options.add_argument("--password-store=basic")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.action_chains = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, config.ERROR_CONFIG["timeout_seconds"])
        
        logger.info("Browser initialized with human-like settings")
    
    def move_mouse_like_human(self, target_x: int, target_y: int) -> None:
        """Move mouse to target position with human-like movement"""
        current_pos = pyautogui.position()
        start = (current_pos.x, current_pos.y)
        end = (target_x, target_y)
        
        # Calculate distance and movement parameters
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        if distance < 5:  # Too close, direct movement
            pyautogui.moveTo(target_x, target_y)
            return
        
        # Generate human-like path
        path = HumanMouseMovement.bezier_curve(start, end)
        path = HumanMouseMovement.add_jitter(path)
        
        # Calculate movement timing
        movement_speed = HumanMouseMovement.calculate_movement_speed(distance)
        total_time = distance / (movement_speed * 1000)  # Convert to seconds
        
        # Add potential overshoot
        if random.random() < config.MOUSE_CONFIG["overshoot_probability"]:
            overshoot_distance = random.randint(*config.MOUSE_CONFIG["overshoot_distance"])
            overshoot_x = target_x + random.randint(-overshoot_distance, overshoot_distance)
            overshoot_y = target_y + random.randint(-overshoot_distance, overshoot_distance)
            path.append((overshoot_x, overshoot_y))
            path.append((target_x, target_y))
        
        # Execute movement
        for i, (x, y) in enumerate(path):
            # Add random pauses during movement
            if random.random() < config.MOUSE_CONFIG["pause_probability"]:
                time.sleep(random.uniform(0.01, 0.05))
            
            # Calculate timing for this segment
            segment_time = total_time / len(path)
            pyautogui.moveTo(x, y, duration=segment_time)
        
        # Final position adjustment
        pyautogui.moveTo(target_x, target_y, duration=0.01)
    
    def click_delayed(self, element=None, x: int = None, y: int = None) -> bool:
        """Click with human-like delay and verification"""
        try:
            if element is not None:
                # Get element position
                location = element.location
                size = element.size
                click_x = location['x'] + size['width'] // 2
                click_y = location['y'] + size['height'] // 2
                
                # Move to element first
                self.move_mouse_like_human(click_x, click_y)
                
                # Random pre-click delay
                time.sleep(random.uniform(*config.TIMING_CONFIG["click_delay"]))
                
                # Click the element
                element.click()
                
            elif x is not None and y is not None:
                self.move_mouse_like_human(x, y)
                time.sleep(random.uniform(*config.TIMING_CONFIG["click_delay"]))
                pyautogui.click(x, y)
            
            # Post-click delay
            time.sleep(random.uniform(0.1, 0.3))
            return True
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    def scroll_smoothly(self, direction: str = "down", amount: int = 3) -> None:
        """Scroll page smoothly like a human"""
        scroll_delay = random.uniform(*config.TIMING_CONFIG["scroll_delay"])
        
        for _ in range(amount):
            if direction == "down":
                self.driver.execute_script("window.scrollBy(0, window.innerHeight/4);")
            else:
                self.driver.execute_script("window.scrollBy(0, -window.innerHeight/4);")
            
            time.sleep(scroll_delay)
    
    def wait_for_page_load(self) -> None:
        """Wait for page to load with random timing"""
        base_wait = random.uniform(*config.TIMING_CONFIG["page_load_wait"])
        time.sleep(base_wait)
        
        # Wait for document ready state
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        # Additional random delay
        time.sleep(random.uniform(0.5, 1.5))
    
    def take_screenshot(self, name: str = None) -> str:
        """Take screenshot and save with timestamp"""
        if name is None:
            name = f"screenshot_{self.screenshot_count}"
            self.screenshot_count += 1
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        
        # Create screenshot directory
        screenshot_dir = Path(config.SCREENSHOT_CONFIG["save_directory"])
        daily_dir = screenshot_dir / datetime.now().strftime("%Y-%m-%d")
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = daily_dir / filename
        
        # Take screenshot
        self.driver.save_screenshot(str(filepath))
        logger.info(f"Screenshot saved: {filepath}")
        
        return str(filepath)
    
    def find_element_safely(self, by: By, value: str, timeout: int = 10) -> Optional[object]:
        """Find element with timeout and error handling"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def find_elements_safely(self, by: By, value: str) -> List[object]:
        """Find multiple elements safely"""
        try:
            elements = self.driver.find_elements(by, value)
            return elements
        except NoSuchElementException:
            logger.warning(f"Elements not found: {by}={value}")
            return []
    
    def random_pause_between_tasks(self) -> None:
        """Random pause between tasks as specified in requirements"""
        delay = random.randint(
            config.TIMING_CONFIG["between_tasks_delay"]["min"],
            config.TIMING_CONFIG["between_tasks_delay"]["max"]
        )
        logger.info(f"Pausing for {delay} seconds between tasks...")
        time.sleep(delay)
    
    def navigate_to_url(self, url: str) -> bool:
        """Navigate to URL with human-like behavior"""
        try:
            self.driver.get(url)
            self.wait_for_page_load()
            
            # Random scroll to simulate reading
            if random.random() < 0.3:  # 30% chance to scroll
                self.scroll_smoothly("down", random.randint(1, 2))
                time.sleep(random.uniform(1, 3))
                self.scroll_smoothly("up", 1)
            
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def quit_browser(self) -> None:
        """Safely quit browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

# Human-like typing simulation
class HumanTyping:
    """Simulates human typing patterns"""
    
    @staticmethod
    def type_like_human(element, text: str) -> None:
        """Type text with human-like timing and errors"""
        element.clear()
        
        for char in text:
            # Random typing speed variation
            typing_delay = random.uniform(0.05, 0.15)
            
            # Occasional typos (5% chance)
            if random.random() < 0.05 and char.isalpha():
                # Type wrong character then backspace
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys('\b')  # Backspace
                time.sleep(random.uniform(0.1, 0.2))
            
            element.send_keys(char)
            time.sleep(typing_delay)
        
        # Random pause after typing
        time.sleep(random.uniform(0.2, 0.8))