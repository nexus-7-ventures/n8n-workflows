import time
import json
import pickle
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
import tkinter as tk
from tkinter import messagebox, simpledialog
import pyautogui
import keyboard
import mouse
from PIL import Image, ImageTk, ImageDraw
import logging

from human_automation import HumanBrowserAutomation
from microworkers_config import config

logger = logging.getLogger(__name__)

class MousePatternRecorder:
    """Records mouse movement patterns for training"""
    
    def __init__(self):
        self.recording = False
        self.patterns = []
        self.current_pattern = []
        self.start_time = None
    
    def start_recording(self, pattern_name: str) -> None:
        """Start recording mouse patterns"""
        self.recording = True
        self.current_pattern = []
        self.start_time = time.time()
        
        logger.info(f"Starting pattern recording: {pattern_name}")
        
        # Set up mouse listener
        mouse.on_move(self._record_mouse_movement)
        mouse.on_click(self._record_mouse_click)
        
        print("Recording mouse patterns... Press 'q' to stop recording.")
        
        # Wait for quit signal
        keyboard.wait('q')
        self.stop_recording(pattern_name)
    
    def _record_mouse_movement(self, x: int, y: int) -> None:
        """Record mouse movement event"""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.current_pattern.append({
                'type': 'move',
                'x': x,
                'y': y,
                'timestamp': timestamp
            })
    
    def _record_mouse_click(self, x: int, y: int, button: str, pressed: bool) -> None:
        """Record mouse click event"""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.current_pattern.append({
                'type': 'click',
                'x': x,
                'y': y,
                'button': button,
                'pressed': pressed,
                'timestamp': timestamp
            })
    
    def stop_recording(self, pattern_name: str) -> None:
        """Stop recording and save pattern"""
        self.recording = False
        mouse.unhook_all()
        
        if self.current_pattern:
            pattern_data = {
                'name': pattern_name,
                'events': self.current_pattern,
                'duration': time.time() - self.start_time,
                'recorded_at': datetime.now().isoformat()
            }
            
            self.patterns.append(pattern_data)
            self.save_patterns()
            
            logger.info(f"Pattern '{pattern_name}' recorded with {len(self.current_pattern)} events")
            print(f"Pattern '{pattern_name}' saved successfully!")
        else:
            print("No pattern data recorded.")
    
    def save_patterns(self) -> None:
        """Save recorded patterns to file"""
        patterns_dir = Path("./training_data/patterns")
        patterns_dir.mkdir(parents=True, exist_ok=True)
        
        pattern_file = patterns_dir / "mouse_patterns.json"
        
        with open(pattern_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def load_patterns(self) -> List[Dict]:
        """Load saved patterns"""
        patterns_file = Path("./training_data/patterns/mouse_patterns.json")
        
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                self.patterns = json.load(f)
        
        return self.patterns

class ClickTargetTrainer:
    """Trains click target identification"""
    
    def __init__(self, automation: HumanBrowserAutomation):
        self.automation = automation
        self.targets = []
        self.training_active = False
    
    def start_target_training(self) -> None:
        """Start interactive target training"""
        self.training_active = True
        
        print("\n=== Click Target Training ===")
        print("Instructions:")
        print("1. Navigate to the Microworkers page")
        print("2. Press 'c' over elements you want to click")
        print("3. Press 'r' over elements to AVOID (like Remove buttons)")
        print("4. Press 'q' to finish training")
        print("5. Use mouse wheel to scroll and explore")
        
        # Set up hotkeys
        keyboard.on_press_key('c', self._mark_click_target)
        keyboard.on_press_key('r', self._mark_avoid_target)
        
        # Wait for completion
        keyboard.wait('q')
        self.stop_target_training()
    
    def _mark_click_target(self, event) -> None:
        """Mark element as click target"""
        if self.training_active:
            x, y = pyautogui.position()
            element_info = self._capture_element_info(x, y)
            
            self.targets.append({
                'type': 'click_target',
                'x': x,
                'y': y,
                'element_info': element_info,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✓ Click target marked at ({x}, {y})")
            self._visual_feedback(x, y, 'green')
    
    def _mark_avoid_target(self, event) -> None:
        """Mark element to avoid"""
        if self.training_active:
            x, y = pyautogui.position()
            element_info = self._capture_element_info(x, y)
            
            self.targets.append({
                'type': 'avoid_target',
                'x': x,
                'y': y,
                'element_info': element_info,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✗ Avoid target marked at ({x}, {y})")
            self._visual_feedback(x, y, 'red')
    
    def _capture_element_info(self, x: int, y: int) -> Dict:
        """Capture information about element at coordinates"""
        try:
            # Try to get element from browser
            element = self.automation.driver.execute_script(
                "return document.elementFromPoint(arguments[0], arguments[1]);",
                x, y
            )
            
            if element:
                return {
                    'tag_name': element.tag_name,
                    'class_name': element.get_attribute('class'),
                    'id': element.get_attribute('id'),
                    'text': element.text[:100],  # First 100 chars
                    'href': element.get_attribute('href')
                }
        except Exception as e:
            logger.warning(f"Could not capture element info: {e}")
        
        return {'x': x, 'y': y}
    
    def _visual_feedback(self, x: int, y: int, color: str) -> None:
        """Show visual feedback for marked targets"""
        # Take screenshot for overlay
        screenshot = pyautogui.screenshot()
        draw = ImageDraw.Draw(screenshot)
        
        # Draw circle around target
        radius = 20
        if color == 'green':
            circle_color = (0, 255, 0)
        else:
            circle_color = (255, 0, 0)
        
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                    outline=circle_color, width=3)
        
        # Save feedback image
        feedback_dir = Path("./training_data/feedback")
        feedback_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot.save(feedback_dir / f"target_{color}_{timestamp}.png")
    
    def stop_target_training(self) -> None:
        """Stop target training and save data"""
        self.training_active = False
        keyboard.unhook_all()
        
        if self.targets:
            self.save_targets()
            logger.info(f"Target training completed with {len(self.targets)} targets")
            print(f"Training completed! {len(self.targets)} targets recorded.")
        else:
            print("No targets recorded.")
    
    def save_targets(self) -> None:
        """Save target data to file"""
        targets_dir = Path("./training_data/targets")
        targets_dir.mkdir(parents=True, exist_ok=True)
        
        targets_file = targets_dir / "click_targets.json"
        
        with open(targets_file, 'w') as f:
            json.dump(self.targets, f, indent=2)

class PageLayoutLearner:
    """Learns page layouts and element positions"""
    
    def __init__(self, automation: HumanBrowserAutomation):
        self.automation = automation
        self.layouts = {}
    
    def learn_page_layout(self, page_name: str) -> Dict:
        """Learn and save page layout"""
        try:
            # Take screenshot
            screenshot_path = self.automation.take_screenshot(f"layout_{page_name}")
            
            # Get page elements
            elements = self.automation.driver.find_elements("xpath", "//*")
            
            layout_data = {
                'page_name': page_name,
                'url': self.automation.driver.current_url,
                'screenshot_path': screenshot_path,
                'elements': [],
                'learned_at': datetime.now().isoformat()
            }
            
            # Analyze key elements
            for element in elements[:50]:  # Limit to first 50 elements
                try:
                    element_data = {
                        'tag_name': element.tag_name,
                        'location': element.location,
                        'size': element.size,
                        'text': element.text[:50] if element.text else '',
                        'class_name': element.get_attribute('class'),
                        'id': element.get_attribute('id')
                    }
                    layout_data['elements'].append(element_data)
                except Exception:
                    continue
            
            self.layouts[page_name] = layout_data
            self.save_layouts()
            
            logger.info(f"Page layout learned for '{page_name}' with {len(layout_data['elements'])} elements")
            return layout_data
            
        except Exception as e:
            logger.error(f"Failed to learn page layout: {e}")
            return {}
    
    def save_layouts(self) -> None:
        """Save learned layouts to file"""
        layouts_dir = Path("./training_data/layouts")
        layouts_dir.mkdir(parents=True, exist_ok=True)
        
        layouts_file = layouts_dir / "page_layouts.json"
        
        with open(layouts_file, 'w') as f:
            json.dump(self.layouts, f, indent=2)

class TrainingGUI:
    """GUI interface for training configuration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Microworkers Training Interface")
        self.root.geometry("600x500")
        
        self.automation = None
        self.setup_gui()
    
    def setup_gui(self) -> None:
        """Set up the GUI interface"""
        # Main title
        title_label = tk.Label(self.root, text="Microworkers Automation Training", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status frame
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=10, fill='x')
        
        self.status_label = tk.Label(self.status_frame, text="Status: Ready for training")
        self.status_label.pack()
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=20)
        
        # Training buttons
        tk.Button(buttons_frame, text="Start Browser Session", 
                 command=self.start_browser, bg='lightblue').pack(pady=5, fill='x')
        
        tk.Button(buttons_frame, text="Record Mouse Patterns", 
                 command=self.record_patterns, bg='lightgreen').pack(pady=5, fill='x')
        
        tk.Button(buttons_frame, text="Train Click Targets", 
                 command=self.train_targets, bg='lightyellow').pack(pady=5, fill='x')
        
        tk.Button(buttons_frame, text="Learn Page Layouts", 
                 command=self.learn_layouts, bg='lightcoral').pack(pady=5, fill='x')
        
        tk.Button(buttons_frame, text="View Training Data", 
                 command=self.view_training_data, bg='lightgray').pack(pady=5, fill='x')
        
        tk.Button(buttons_frame, text="Exit Training", 
                 command=self.exit_training, bg='lightpink').pack(pady=20, fill='x')
        
        # Progress text area
        self.progress_text = tk.Text(self.root, height=15, width=70)
        self.progress_text.pack(pady=10, fill='both', expand=True)
        
        # Scrollbar for text area
        scrollbar = tk.Scrollbar(self.progress_text)
        scrollbar.pack(side='right', fill='y')
        self.progress_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.progress_text.yview)
    
    def log_message(self, message: str) -> None:
        """Add message to progress text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.progress_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.progress_text.see(tk.END)
        self.root.update()
    
    def start_browser(self) -> None:
        """Start browser session for training"""
        try:
            self.log_message("Starting browser session...")
            self.automation = HumanBrowserAutomation()
            
            # Navigate to Microworkers
            self.automation.navigate_to_url(config.MICROWORKERS_BASE_URL)
            
            self.log_message("Browser session started. Ready for training.")
            self.status_label.config(text="Status: Browser session active")
            
        except Exception as e:
            self.log_message(f"Error starting browser: {e}")
            messagebox.showerror("Error", f"Failed to start browser: {e}")
    
    def record_patterns(self) -> None:
        """Start pattern recording"""
        if not self.automation:
            messagebox.showwarning("Warning", "Please start browser session first!")
            return
        
        pattern_name = simpledialog.askstring("Pattern Name", "Enter pattern name:")
        if not pattern_name:
            return
        
        self.log_message(f"Starting pattern recording: {pattern_name}")
        self.log_message("Minimize this window and perform mouse actions...")
        self.log_message("Press 'q' when finished recording.")
        
        # Start recording in separate thread
        recorder = MousePatternRecorder()
        threading.Thread(target=recorder.start_recording, args=(pattern_name,)).start()
    
    def train_targets(self) -> None:
        """Start target training"""
        if not self.automation:
            messagebox.showwarning("Warning", "Please start browser session first!")
            return
        
        self.log_message("Starting click target training...")
        self.log_message("Minimize this window and use hotkeys:")
        self.log_message("- Press 'c' over elements to CLICK")
        self.log_message("- Press 'r' over elements to AVOID")
        self.log_message("- Press 'q' when finished")
        
        # Start training in separate thread
        trainer = ClickTargetTrainer(self.automation)
        threading.Thread(target=trainer.start_target_training).start()
    
    def learn_layouts(self) -> None:
        """Learn page layouts"""
        if not self.automation:
            messagebox.showwarning("Warning", "Please start browser session first!")
            return
        
        page_name = simpledialog.askstring("Page Name", "Enter page name (e.g., 'tasks_page'):")
        if not page_name:
            return
        
        self.log_message(f"Learning layout for: {page_name}")
        
        learner = PageLayoutLearner(self.automation)
        layout_data = learner.learn_page_layout(page_name)
        
        if layout_data:
            self.log_message(f"Layout learned with {len(layout_data['elements'])} elements")
        else:
            self.log_message("Failed to learn layout")
    
    def view_training_data(self) -> None:
        """View collected training data"""
        try:
            training_dir = Path("./training_data")
            
            if not training_dir.exists():
                self.log_message("No training data found.")
                return
            
            self.log_message("=== Training Data Summary ===")
            
            # Check patterns
            patterns_file = training_dir / "patterns" / "mouse_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns = json.load(f)
                self.log_message(f"Mouse patterns: {len(patterns)}")
            
            # Check targets
            targets_file = training_dir / "targets" / "click_targets.json"
            if targets_file.exists():
                with open(targets_file, 'r') as f:
                    targets = json.load(f)
                self.log_message(f"Click targets: {len(targets)}")
            
            # Check layouts
            layouts_file = training_dir / "layouts" / "page_layouts.json"
            if layouts_file.exists():
                with open(layouts_file, 'r') as f:
                    layouts = json.load(f)
                self.log_message(f"Page layouts: {len(layouts)}")
            
        except Exception as e:
            self.log_message(f"Error viewing training data: {e}")
    
    def exit_training(self) -> None:
        """Exit training interface"""
        if self.automation:
            self.automation.quit_browser()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self) -> None:
        """Run the training GUI"""
        self.root.mainloop()

class UserGuidedTraining:
    """Main class for user-guided training mode"""
    
    def __init__(self):
        self.gui = TrainingGUI()
    
    def start_training_mode(self) -> None:
        """Start the complete training mode"""
        print("\n" + "="*50)
        print("MICROWORKERS AUTOMATION TRAINING MODE")
        print("="*50)
        print("\nThis training mode will help you set up the automation system.")
        print("You'll be able to:")
        print("1. Record natural mouse movement patterns")
        print("2. Train the system on which elements to click")
        print("3. Teach page layouts and navigation")
        print("4. Configure behavior patterns")
        print("\nStarting training interface...")
        
        # Run the GUI
        self.gui.run()

# Main training functions
def user_guided_training_mode() -> None:
    """Entry point for user-guided training"""
    trainer = UserGuidedTraining()
    trainer.start_training_mode()

def start_here_workflow_guide() -> Dict[str, str]:
    """Initiate with training setup guide"""
    return {
        "status": "training_ready",
        "message": "Training mode initialized. Use user_guided_training_mode() to start.",
        "next_steps": [
            "1. Run user_guided_training_mode()",
            "2. Train mouse patterns and click targets",
            "3. Configure page layouts",
            "4. Test automation behavior"
        ]
    }

if __name__ == "__main__":
    user_guided_training_mode()