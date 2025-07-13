#!/usr/bin/env python3
"""
OCR Reader for Screen Text Extraction
Uses tesseract/pillow to read visible screen text and extract Maps Search information.
"""

import time
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pyautogui
import numpy as np
import cv2


@dataclass
class QueryInfo:
    """Information about the current search query"""
    query: str
    location: Optional[str] = None
    search_type: Optional[str] = None
    user_location: Optional[str] = None


@dataclass
class MapResult:
    """Information about a map search result"""
    name: str
    address: str
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    distance: Optional[str] = None
    category: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[str] = None
    position: Optional[Tuple[int, int]] = None


class OCRReader:
    """Screen OCR reader for Maps Search Evaluation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configure tesseract if needed
        try:
            # Test tesseract installation
            pytesseract.get_tesseract_version()
            self.logger.info("Tesseract OCR initialized successfully")
        except Exception as e:
            self.logger.warning(f"Tesseract not properly configured: {e}")
            self.logger.info("OCR functionality may be limited")
        
        # Common patterns for extraction
        self.query_patterns = {
            'search_box': [
                r'Search Google Maps',
                r'Search here',
                r'Find a place',
                r'What are you looking for\?'
            ],
            'query_text': [
                r'Showing results for "([^"]+)"',
                r'Results for ([^\n]+)',
                r'Search: ([^\n]+)',
                r'"([^"]+)" - Google Maps'
            ]
        }
        
        self.result_patterns = {
            'business_name': [
                r'^([A-Z][A-Za-z\s&\-\'\.]+)$',
                r'([A-Z][A-Za-z\s&\-\'\.]+)\s+\d+\.\d+★',
                r'([A-Z][A-Za-z\s&\-\'\.]+)\s+\(\d+\)'
            ],
            'address': [
                r'(\d+[A-Za-z]?\s+[A-Za-z\s]+(?:St|Ave|Rd|Blvd|Dr|Ln|Way|Ct|Pl)\.?)',
                r'([A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5})',
                r'([A-Za-z\s]+\d{5})'
            ],
            'rating': [
                r'(\d+\.\d+)★',
                r'(\d+\.\d+)\s*stars?',
                r'Rating:\s*(\d+\.\d+)'
            ],
            'reviews': [
                r'\((\d+)\)',
                r'(\d+)\s+reviews?',
                r'(\d+)\s+ratings?'
            ],
            'distance': [
                r'(\d+\.\d+)\s*mi',
                r'(\d+\.\d+)\s*km',
                r'(\d+)\s*min\s+drive'
            ],
            'phone': [
                r'\((\d{3})\)\s*(\d{3})-(\d{4})',
                r'(\d{3})-(\d{3})-(\d{4})',
                r'(\d{10})'
            ]
        }
        
        self.logger.info("OCR Reader initialized")
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """Capture screen or screen region"""
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            return screenshot
        except Exception as e:
            self.logger.error(f"Failed to capture screen: {e}")
            return None
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply filters for better text recognition
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            return image
        except Exception as e:
            self.logger.error(f"Failed to preprocess image: {e}")
            return image
    
    def extract_text_from_image(self, image: Image.Image, config: str = '--psm 6') -> str:
        """Extract text from image using OCR"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=config)
            
            return text.strip()
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def read_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Read text from screen"""
        self.logger.info("Reading screen content")
        
        # Capture screen
        screenshot = self.capture_screen(region)
        if not screenshot:
            return ""
        
        # Extract text
        text = self.extract_text_from_image(screenshot)
        
        self.logger.info(f"Extracted {len(text)} characters from screen")
        return text
    
    def extract_query_info(self, screen_text: str) -> QueryInfo:
        """Extract query information from screen text"""
        self.logger.info("Extracting query information")
        
        query_info = QueryInfo(query="Unknown")
        
        # Try to find query text using patterns
        for pattern in self.query_patterns['query_text']:
            match = re.search(pattern, screen_text, re.IGNORECASE)
            if match:
                query_info.query = match.group(1).strip()
                break
        
        # Try to identify search type
        query_lower = query_info.query.lower()
        if any(word in query_lower for word in ['restaurant', 'food', 'eat', 'dine']):
            query_info.search_type = 'restaurant'
        elif any(word in query_lower for word in ['gas', 'station', 'fuel']):
            query_info.search_type = 'gas_station'
        elif any(word in query_lower for word in ['hotel', 'stay', 'accommodation']):
            query_info.search_type = 'hotel'
        elif any(word in query_lower for word in ['shop', 'store', 'buy']):
            query_info.search_type = 'shopping'
        else:
            query_info.search_type = 'general'
        
        # Extract location context
        location_match = re.search(r'near\s+([A-Za-z\s,]+)', screen_text, re.IGNORECASE)
        if location_match:
            query_info.location = location_match.group(1).strip()
        
        self.logger.info(f"Query: {query_info.query}, Type: {query_info.search_type}")
        return query_info
    
    def extract_map_results(self, screen_text: str) -> List[MapResult]:
        """Extract map search results from screen text"""
        self.logger.info("Extracting map results")
        
        results = []
        lines = screen_text.split('\n')
        
        current_result = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to identify business name
            name_match = self._find_pattern_match(line, self.result_patterns['business_name'])
            if name_match and len(name_match) > 3:  # Minimum length filter
                # Save previous result if exists
                if current_result:
                    results.append(current_result)
                
                # Start new result
                current_result = MapResult(name=name_match)
                continue
            
            # If we have a current result, try to extract more info
            if current_result:
                # Try to extract address
                address_match = self._find_pattern_match(line, self.result_patterns['address'])
                if address_match and not current_result.address:
                    current_result.address = address_match
                
                # Try to extract rating
                rating_match = self._find_pattern_match(line, self.result_patterns['rating'])
                if rating_match:
                    try:
                        current_result.rating = float(rating_match)
                    except ValueError:
                        pass
                
                # Try to extract reviews count
                reviews_match = self._find_pattern_match(line, self.result_patterns['reviews'])
                if reviews_match:
                    try:
                        current_result.reviews_count = int(reviews_match)
                    except ValueError:
                        pass
                
                # Try to extract distance
                distance_match = self._find_pattern_match(line, self.result_patterns['distance'])
                if distance_match:
                    current_result.distance = distance_match
                
                # Try to extract phone
                phone_match = self._find_pattern_match(line, self.result_patterns['phone'])
                if phone_match:
                    current_result.phone = phone_match
        
        # Add the last result
        if current_result:
            results.append(current_result)
        
        # Filter out incomplete results
        valid_results = [r for r in results if r.name and r.name != "Unknown"]
        
        self.logger.info(f"Extracted {len(valid_results)} valid results")
        return valid_results
    
    def _find_pattern_match(self, text: str, patterns: List[str]) -> Optional[str]:
        """Find first matching pattern in text"""
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        return None
    
    def get_search_box_region(self) -> Tuple[int, int, int, int]:
        """Get approximate search box region"""
        screen_width, screen_height = pyautogui.size()
        
        # Common search box location (top center)
        x = screen_width // 4
        y = 50
        width = screen_width // 2
        height = 100
        
        return (x, y, width, height)
    
    def get_results_region(self) -> Tuple[int, int, int, int]:
        """Get approximate results region"""
        screen_width, screen_height = pyautogui.size()
        
        # Left sidebar typically contains results
        x = 0
        y = 150
        width = 400
        height = screen_height - 200
        
        return (x, y, width, height)
    
    def get_map_region(self) -> Tuple[int, int, int, int]:
        """Get approximate map region"""
        screen_width, screen_height = pyautogui.size()
        
        # Right side typically contains map
        x = 400
        y = 150
        width = screen_width - 400
        height = screen_height - 200
        
        return (x, y, width, height)
    
    def read_search_box(self) -> str:
        """Read text from search box area"""
        region = self.get_search_box_region()
        return self.read_screen(region)
    
    def read_results_sidebar(self) -> str:
        """Read text from results sidebar"""
        region = self.get_results_region()
        return self.read_screen(region)
    
    def read_map_area(self) -> str:
        """Read text from map area"""
        region = self.get_map_region()
        return self.read_screen(region)
    
    def find_text_on_screen(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Tuple[int, int]]:
        """Find specific text on screen and return its position"""
        self.logger.info(f"Searching for text: {target_text}")
        
        screen_text = self.read_screen(region)
        
        if target_text.lower() in screen_text.lower():
            # For now, return approximate position
            # More sophisticated implementation would use OCR bounding boxes
            screen_width, screen_height = pyautogui.size()
            return (screen_width // 2, screen_height // 2)
        
        return None
    
    def detect_rating_interface(self) -> Dict[str, Any]:
        """Detect rating interface elements"""
        self.logger.info("Detecting rating interface")
        
        # Read screen
        screen_text = self.read_screen()
        
        # Look for rating-related text
        rating_keywords = [
            'rate', 'rating', 'excellent', 'good', 'fair', 'poor',
            'navigational', 'relevant', 'not relevant', 'off-topic'
        ]
        
        detected_elements = {
            'has_rating_interface': False,
            'rating_options': [],
            'comment_box': False
        }
        
        for keyword in rating_keywords:
            if keyword.lower() in screen_text.lower():
                detected_elements['has_rating_interface'] = True
                detected_elements['rating_options'].append(keyword)
        
        # Look for comment box indicators
        comment_keywords = ['comment', 'feedback', 'notes', 'reason']
        for keyword in comment_keywords:
            if keyword.lower() in screen_text.lower():
                detected_elements['comment_box'] = True
        
        return detected_elements
    
    def get_visible_business_info(self) -> Dict[str, Any]:
        """Get comprehensive business information visible on screen"""
        self.logger.info("Extracting visible business information")
        
        # Read different screen regions
        search_text = self.read_search_box()
        results_text = self.read_results_sidebar()
        map_text = self.read_map_area()
        
        # Combine all text
        full_text = f"{search_text}\n{results_text}\n{map_text}"
        
        # Extract information
        query_info = self.extract_query_info(full_text)
        map_results = self.extract_map_results(full_text)
        
        return {
            'query': query_info,
            'results': map_results,
            'full_text': full_text,
            'timestamp': time.time()
        }
    
    def save_screenshot(self, filename: str, region: Optional[Tuple[int, int, int, int]] = None):
        """Save screenshot for debugging"""
        try:
            screenshot = self.capture_screen(region)
            if screenshot:
                screenshot.save(filename)
                self.logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save screenshot: {e}")
    
    def test_ocr_accuracy(self) -> Dict[str, Any]:
        """Test OCR accuracy on current screen"""
        self.logger.info("Testing OCR accuracy")
        
        # Capture screen
        screenshot = self.capture_screen()
        if not screenshot:
            return {'error': 'Failed to capture screen'}
        
        # Test different OCR configurations
        configs = [
            '--psm 6',  # Uniform block of text
            '--psm 7',  # Single text line
            '--psm 8',  # Single word
            '--psm 13'  # Raw line
        ]
        
        results = {}
        for config in configs:
            try:
                text = self.extract_text_from_image(screenshot, config)
                results[config] = {
                    'text_length': len(text),
                    'word_count': len(text.split()),
                    'confidence': 'unknown'  # Would need tesseract data for actual confidence
                }
            except Exception as e:
                results[config] = {'error': str(e)}
        
        return results