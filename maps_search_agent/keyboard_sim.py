#!/usr/bin/env python3
"""
Keyboard Simulator with Human-like Typing Behavior
Includes realistic typing patterns, typos, corrections, and timing variations.
"""

import time
import random
import pyautogui
import string
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass


@dataclass
class TypingProfile:
    """Human-like typing behavior profile"""
    base_wpm: int = 65  # Words per minute
    typo_rate: float = 0.03  # 3% typo rate
    pause_probability: float = 0.1  # 10% chance of pause
    thinking_pause_probability: float = 0.05  # 5% chance of longer pause
    backspace_delay: float = 0.1
    min_key_delay: float = 0.05
    max_key_delay: float = 0.15


class KeyboardSimulator:
    """Human-like keyboard simulator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.profile = TypingProfile()
        
        # Common typos mapping
        self.typo_patterns = {
            'a': ['s', 'q', 'w'],
            'b': ['v', 'g', 'h', 'n'],
            'c': ['x', 'd', 'f', 'v'],
            'd': ['s', 'e', 'r', 'f', 'c'],
            'e': ['w', 'r', 's', 'd'],
            'f': ['d', 'g', 'r', 't', 'v', 'c'],
            'g': ['f', 'h', 't', 'y', 'b', 'v'],
            'h': ['g', 'j', 'y', 'u', 'n', 'b'],
            'i': ['u', 'o', 'j', 'k'],
            'j': ['h', 'k', 'u', 'i', 'm', 'n'],
            'k': ['j', 'l', 'i', 'o', 'n', 'm'],
            'l': ['k', 'o', 'p'],
            'm': ['n', 'j', 'k'],
            'n': ['b', 'm', 'h', 'j'],
            'o': ['i', 'p', 'k', 'l'],
            'p': ['o', 'l'],
            'q': ['w', 'a'],
            'r': ['e', 't', 'd', 'f'],
            's': ['a', 'd', 'w', 'e'],
            't': ['r', 'y', 'f', 'g'],
            'u': ['y', 'i', 'h', 'j'],
            'v': ['c', 'b', 'f', 'g'],
            'w': ['q', 'e', 'a', 's'],
            'x': ['z', 'c', 's', 'd'],
            'y': ['t', 'u', 'g', 'h'],
            'z': ['x', 'a', 's']
        }
        
        # Words that commonly get typos
        self.common_typos = {
            'the': 'teh',
            'and': 'adn',
            'for': 'fro',
            'you': 'yuo',
            'this': 'thsi',
            'that': 'taht',
            'with': 'wiht',
            'have': 'ahve',
            'from': 'form',
            'they': 'tehy'
        }
        
        self.logger.info("Keyboard simulator initialized")
    
    def _calculate_key_delay(self) -> float:
        """Calculate realistic delay between keystrokes"""
        # Base delay from WPM
        base_delay = 60.0 / (self.profile.base_wpm * 5)  # 5 chars per word average
        
        # Add variation
        variation = random.uniform(0.8, 1.2)
        delay = base_delay * variation
        
        # Ensure within bounds
        return max(self.profile.min_key_delay, 
                  min(self.profile.max_key_delay, delay))
    
    def _should_make_typo(self, char: str) -> bool:
        """Determine if a typo should be made"""
        return random.random() < self.profile.typo_rate
    
    def _generate_typo(self, char: str) -> str:
        """Generate a realistic typo for the given character"""
        char_lower = char.lower()
        
        if char_lower in self.typo_patterns:
            typo_char = random.choice(self.typo_patterns[char_lower])
            # Preserve original case
            return typo_char.upper() if char.isupper() else typo_char
        else:
            # Random adjacent key
            keyboard_layout = 'qwertyuiopasdfghjklzxcvbnm'
            return random.choice(keyboard_layout)
    
    def _type_character(self, char: str) -> bool:
        """Type a single character, returns True if typo was made"""
        typo_made = False
        
        # Check for typo
        if self._should_make_typo(char):
            typo_char = self._generate_typo(char)
            pyautogui.write(typo_char)
            typo_made = True
            
            # Brief pause before correction
            time.sleep(random.uniform(0.1, 0.3))
            
            # Correct the typo
            pyautogui.press('backspace')
            time.sleep(self.profile.backspace_delay)
        
        # Type the correct character
        pyautogui.write(char)
        time.sleep(self._calculate_key_delay())
        
        return typo_made
    
    def _handle_word_typo(self, word: str) -> str:
        """Handle common word-level typos"""
        word_lower = word.lower()
        
        if word_lower in self.common_typos and random.random() < 0.1:
            return self.common_typos[word_lower]
        
        return word
    
    def _thinking_pause(self):
        """Simulate thinking pause"""
        if random.random() < self.profile.thinking_pause_probability:
            pause_duration = random.uniform(1.0, 3.0)
            time.sleep(pause_duration)
    
    def _typing_pause(self):
        """Simulate brief typing pause"""
        if random.random() < self.profile.pause_probability:
            pause_duration = random.uniform(0.2, 0.8)
            time.sleep(pause_duration)
    
    def type_text(self, text: str, natural_pauses: bool = True):
        """Type text with human-like behavior"""
        self.logger.info(f"Typing text: {text[:50]}...")
        
        words = text.split()
        
        for i, word in enumerate(words):
            # Handle word-level typos
            word_to_type = self._handle_word_typo(word)
            
            # Type each character
            for char in word_to_type:
                self._type_character(char)
                
                # Random micro-pauses
                if natural_pauses:
                    self._typing_pause()
            
            # Space between words (except last word)
            if i < len(words) - 1:
                pyautogui.write(' ')
                time.sleep(self._calculate_key_delay())
                
                # Thinking pause between words occasionally
                if natural_pauses:
                    self._thinking_pause()
    
    def type_comment(self, comment: str):
        """Type a comment with appropriate pauses and corrections"""
        self.logger.info(f"Typing comment: {comment[:30]}...")
        
        # Brief pause before starting
        time.sleep(random.uniform(0.5, 1.5))
        
        # Type the comment
        self.type_text(comment, natural_pauses=True)
        
        # Brief pause after typing
        time.sleep(random.uniform(0.3, 0.8))
    
    def simulate_correction(self, text: str):
        """Simulate typing text with corrections"""
        self.logger.info("Simulating text correction")
        
        # Type some text
        partial_text = text[:len(text)//2]
        self.type_text(partial_text)
        
        # Pause and "realize" mistake
        time.sleep(random.uniform(1.0, 2.0))
        
        # Backspace to correct
        backspace_count = random.randint(3, 10)
        for _ in range(backspace_count):
            pyautogui.press('backspace')
            time.sleep(self.profile.backspace_delay)
        
        # Type the corrected version
        remaining_text = text[len(text)//2 - backspace_count:]
        self.type_text(remaining_text)
    
    def simulate_hesitation(self):
        """Simulate typing hesitation"""
        self.logger.info("Simulating typing hesitation")
        
        # Type a few characters
        hesitation_text = random.choice(['I think', 'Well', 'Maybe', 'Actually'])
        self.type_text(hesitation_text)
        
        # Pause
        time.sleep(random.uniform(1.0, 2.5))
        
        # Delete and start over
        for _ in range(len(hesitation_text)):
            pyautogui.press('backspace')
            time.sleep(self.profile.backspace_delay)
        
        time.sleep(random.uniform(0.5, 1.0))
    
    def type_with_backtrack(self, text: str):
        """Type text with realistic backtracking"""
        words = text.split()
        typed_words = []
        
        for word in words:
            # Sometimes backtrack to previous word
            if len(typed_words) > 0 and random.random() < 0.1:
                # Go back to previous word
                chars_to_delete = len(typed_words[-1]) + 1  # +1 for space
                for _ in range(chars_to_delete):
                    pyautogui.press('backspace')
                    time.sleep(self.profile.backspace_delay)
                
                # Retype previous word
                prev_word = typed_words[-1]
                self.type_text(prev_word + ' ')
            
            # Type current word
            self.type_text(word)
            typed_words.append(word)
            
            # Add space if not last word
            if word != words[-1]:
                pyautogui.write(' ')
                time.sleep(self._calculate_key_delay())
    
    def simulate_natural_typing_flow(self, text: str):
        """Simulate natural typing flow with various behaviors"""
        behaviors = [
            lambda: self.type_text(text),
            lambda: self.type_with_backtrack(text),
            lambda: self.simulate_correction(text),
        ]
        
        # Sometimes add hesitation at the beginning
        if random.random() < 0.2:
            self.simulate_hesitation()
        
        # Choose typing behavior
        behavior = random.choice(behaviors)
        behavior()
    
    def press_key(self, key: str, delay: Optional[float] = None):
        """Press a single key with optional delay"""
        if delay is None:
            delay = self._calculate_key_delay()
        
        pyautogui.press(key)
        time.sleep(delay)
    
    def key_combination(self, keys: List[str]):
        """Press key combination (e.g., Ctrl+C)"""
        self.logger.info(f"Pressing key combination: {'+'.join(keys)}")
        
        # Press keys in sequence
        for key in keys:
            pyautogui.keyDown(key)
            time.sleep(0.05)
        
        # Release keys in reverse order
        for key in reversed(keys):
            pyautogui.keyUp(key)
            time.sleep(0.05)
    
    def simulate_paste(self, text: str):
        """Simulate paste operation"""
        self.logger.info("Simulating paste operation")
        
        # Simulate Ctrl+V with slight delay
        self.key_combination(['ctrl', 'v'])
        time.sleep(random.uniform(0.1, 0.3))
    
    def clear_field(self):
        """Clear current text field"""
        self.logger.info("Clearing text field")
        
        # Select all and delete
        self.key_combination(['ctrl', 'a'])
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)
    
    def get_typing_speed(self) -> float:
        """Get current typing speed in WPM"""
        return self.profile.base_wpm
    
    def set_typing_speed(self, wpm: int):
        """Set typing speed"""
        self.profile.base_wpm = max(30, min(120, wpm))  # Realistic range
        self.logger.info(f"Typing speed set to {self.profile.base_wpm} WPM")
    
    def set_typo_rate(self, rate: float):
        """Set typo rate (0.0 to 1.0)"""
        self.profile.typo_rate = max(0.0, min(1.0, rate))
        self.logger.info(f"Typo rate set to {self.profile.typo_rate:.1%}")
    
    def emergency_stop(self):
        """Emergency stop for keyboard operations"""
        self.logger.warning("Emergency stop activated")
        # Clear any held keys
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('alt')
        pyautogui.keyUp('shift')