#!/usr/bin/env python3
"""
Task Logger for Maps Search Evaluation
Saves all task output to ratings_log.csv with proper CSV formatting and data management.
"""

import csv
import time
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import os


class TaskLogger:
    """Logs all Maps Search Evaluation tasks to CSV"""
    
    def __init__(self, log_file: str = "ratings_log.csv"):
        self.logger = logging.getLogger(__name__)
        self.log_file = Path(log_file)
        
        # CSV headers
        self.headers = [
            'timestamp',
            'datetime',
            'query',
            'relevance_rating',
            'demotion_reason',
            'comment',
            'screenshot_before',
            'screenshot_after',
            'duration_seconds',
            'confidence_score',
            'user_intent',
            'data_issues',
            'reasoning'
        ]
        
        # Initialize CSV file
        self.initialize_csv()
        
        # Track session statistics
        self.session_stats = {
            'total_tasks': 0,
            'rating_distribution': {},
            'session_start': time.time(),
            'last_task_time': 0
        }
        
        self.logger.info(f"Task logger initialized: {self.log_file}")
    
    def initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not self.log_file.exists():
            try:
                with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                    writer.writeheader()
                self.logger.info("CSV file initialized with headers")
            except Exception as e:
                self.logger.error(f"Failed to initialize CSV file: {e}")
                raise
    
    def log_task(self, task_data: Dict[str, Any]):
        """Log a completed task to CSV"""
        try:
            # Prepare data for CSV
            csv_row = self.prepare_csv_row(task_data)
            
            # Write to CSV
            with open(self.log_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                writer.writerow(csv_row)
            
            # Update session statistics
            self.update_session_stats(task_data)
            
            self.logger.info(f"Task logged: {task_data.get('query', 'Unknown')}")
            
        except Exception as e:
            self.logger.error(f"Failed to log task: {e}")
            # Don't raise - logging failures shouldn't stop the agent
    
    def prepare_csv_row(self, task_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare task data for CSV format"""
        timestamp = task_data.get('timestamp', time.time())
        
        # Handle data issues (convert list to string)
        data_issues = task_data.get('data_issues', [])
        if isinstance(data_issues, list):
            data_issues_str = '; '.join(data_issues) if data_issues else ''
        else:
            data_issues_str = str(data_issues)
        
        csv_row = {
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'query': self.clean_csv_value(task_data.get('query', '')),
            'relevance_rating': task_data.get('rating', ''),
            'demotion_reason': self.clean_csv_value(task_data.get('demotion_reason', '')),
            'comment': self.clean_csv_value(task_data.get('comment', '')),
            'screenshot_before': task_data.get('screenshot_before', ''),
            'screenshot_after': task_data.get('screenshot_after', ''),
            'duration_seconds': task_data.get('duration', 0),
            'confidence_score': task_data.get('confidence', 0),
            'user_intent': task_data.get('user_intent', ''),
            'data_issues': data_issues_str,
            'reasoning': self.clean_csv_value(task_data.get('reasoning', ''))
        }
        
        return csv_row
    
    def clean_csv_value(self, value: str) -> str:
        """Clean value for CSV format"""
        if not value:
            return ''
        
        # Convert to string and strip whitespace
        value = str(value).strip()
        
        # Remove or replace problematic characters
        value = value.replace('\n', ' ').replace('\r', ' ')
        value = value.replace('\t', ' ')
        
        # Limit length to prevent CSV issues
        if len(value) > 500:
            value = value[:497] + '...'
        
        return value
    
    def update_session_stats(self, task_data: Dict[str, Any]):
        """Update session statistics"""
        self.session_stats['total_tasks'] += 1
        self.session_stats['last_task_time'] = time.time()
        
        # Update rating distribution
        rating = task_data.get('rating', 'unknown')
        if rating not in self.session_stats['rating_distribution']:
            self.session_stats['rating_distribution'][rating] = 0
        self.session_stats['rating_distribution'][rating] += 1
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        current_time = time.time()
        session_duration = current_time - self.session_stats['session_start']
        
        return {
            'total_tasks': self.session_stats['total_tasks'],
            'session_duration_minutes': session_duration / 60,
            'rating_distribution': self.session_stats['rating_distribution'],
            'tasks_per_hour': (self.session_stats['total_tasks'] / session_duration) * 3600 if session_duration > 0 else 0,
            'last_task_time': self.session_stats['last_task_time'],
            'log_file_size': self.get_log_file_size()
        }
    
    def get_log_file_size(self) -> int:
        """Get current log file size in bytes"""
        try:
            return self.log_file.stat().st_size if self.log_file.exists() else 0
        except Exception:
            return 0
    
    def get_recent_tasks(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get tasks from the last N hours"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            recent_tasks = []
            
            with open(self.log_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        timestamp = float(row['timestamp'])
                        if timestamp >= cutoff_time:
                            recent_tasks.append(row)
                    except (ValueError, KeyError):
                        continue
            
            return recent_tasks
        except Exception as e:
            self.logger.error(f"Failed to get recent tasks: {e}")
            return []
    
    def get_rating_summary(self) -> Dict[str, Any]:
        """Get summary of all ratings"""
        try:
            rating_counts = {}
            total_tasks = 0
            
            with open(self.log_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    total_tasks += 1
                    rating = row.get('relevance_rating', 'unknown')
                    rating_counts[rating] = rating_counts.get(rating, 0) + 1
            
            # Calculate percentages
            rating_percentages = {}
            for rating, count in rating_counts.items():
                rating_percentages[rating] = (count / total_tasks) * 100 if total_tasks > 0 else 0
            
            return {
                'total_tasks': total_tasks,
                'rating_counts': rating_counts,
                'rating_percentages': rating_percentages
            }
        except Exception as e:
            self.logger.error(f"Failed to get rating summary: {e}")
            return {'total_tasks': 0, 'rating_counts': {}, 'rating_percentages': {}}
    
    def export_filtered_data(self, output_file: str, filters: Dict[str, Any] = None):
        """Export filtered data to new CSV file"""
        try:
            if filters is None:
                filters = {}
            
            filtered_rows = []
            
            with open(self.log_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Apply filters
                    if self.row_matches_filters(row, filters):
                        filtered_rows.append(row)
            
            # Write filtered data
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                if filtered_rows:
                    writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                    writer.writeheader()
                    writer.writerows(filtered_rows)
            
            self.logger.info(f"Exported {len(filtered_rows)} filtered rows to {output_file}")
            return len(filtered_rows)
            
        except Exception as e:
            self.logger.error(f"Failed to export filtered data: {e}")
            return 0
    
    def row_matches_filters(self, row: Dict[str, str], filters: Dict[str, Any]) -> bool:
        """Check if row matches given filters"""
        for filter_key, filter_value in filters.items():
            if filter_key not in row:
                continue
            
            row_value = row[filter_key]
            
            # Handle different filter types
            if isinstance(filter_value, str):
                if filter_value.lower() not in row_value.lower():
                    return False
            elif isinstance(filter_value, list):
                if row_value not in filter_value:
                    return False
            elif isinstance(filter_value, dict):
                # Handle range filters
                if 'min' in filter_value:
                    try:
                        if float(row_value) < filter_value['min']:
                            return False
                    except ValueError:
                        return False
                if 'max' in filter_value:
                    try:
                        if float(row_value) > filter_value['max']:
                            return False
                    except ValueError:
                        return False
        
        return True
    
    def backup_log_file(self):
        """Create a backup of the current log file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.log_file.parent / f"{self.log_file.stem}_backup_{timestamp}.csv"
            
            # Copy current log to backup
            import shutil
            shutil.copy2(self.log_file, backup_file)
            
            self.logger.info(f"Log file backed up to {backup_file}")
            return backup_file
        except Exception as e:
            self.logger.error(f"Failed to backup log file: {e}")
            return None
    
    def rotate_log_file(self, max_size_mb: int = 10):
        """Rotate log file if it exceeds max size"""
        try:
            current_size_mb = self.get_log_file_size() / (1024 * 1024)
            
            if current_size_mb > max_size_mb:
                # Create backup
                backup_file = self.backup_log_file()
                if backup_file:
                    # Create new log file
                    self.initialize_csv()
                    self.logger.info(f"Log file rotated at {current_size_mb:.2f}MB")
                    return True
        except Exception as e:
            self.logger.error(f"Failed to rotate log file: {e}")
        
        return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from logged data"""
        try:
            tasks = self.get_recent_tasks(hours=24)  # Last 24 hours
            
            if not tasks:
                return {'error': 'No recent tasks found'}
            
            # Calculate metrics
            total_tasks = len(tasks)
            
            # Task rate
            if total_tasks > 1:
                time_span = float(tasks[-1]['timestamp']) - float(tasks[0]['timestamp'])
                tasks_per_hour = (total_tasks / time_span) * 3600 if time_span > 0 else 0
            else:
                tasks_per_hour = 0
            
            # Average duration
            durations = [float(task.get('duration_seconds', 0)) for task in tasks]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Rating distribution
            rating_counts = {}
            for task in tasks:
                rating = task.get('relevance_rating', 'unknown')
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
            
            return {
                'total_tasks_24h': total_tasks,
                'tasks_per_hour': tasks_per_hour,
                'average_duration': avg_duration,
                'rating_distribution': rating_counts,
                'log_file_size_mb': self.get_log_file_size() / (1024 * 1024)
            }
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {'error': str(e)}
    
    def validate_log_integrity(self) -> Dict[str, Any]:
        """Validate log file integrity"""
        try:
            validation_results = {
                'total_rows': 0,
                'valid_rows': 0,
                'invalid_rows': 0,
                'errors': []
            }
            
            with open(self.log_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, 1):
                    validation_results['total_rows'] += 1
                    
                    # Validate required fields
                    if not row.get('timestamp'):
                        validation_results['errors'].append(f"Row {row_num}: Missing timestamp")
                        validation_results['invalid_rows'] += 1
                        continue
                    
                    if not row.get('query'):
                        validation_results['errors'].append(f"Row {row_num}: Missing query")
                        validation_results['invalid_rows'] += 1
                        continue
                    
                    # Validate timestamp format
                    try:
                        float(row['timestamp'])
                    except ValueError:
                        validation_results['errors'].append(f"Row {row_num}: Invalid timestamp format")
                        validation_results['invalid_rows'] += 1
                        continue
                    
                    validation_results['valid_rows'] += 1
            
            validation_results['integrity_score'] = (
                validation_results['valid_rows'] / validation_results['total_rows'] * 100
                if validation_results['total_rows'] > 0 else 0
            )
            
            return validation_results
        except Exception as e:
            self.logger.error(f"Failed to validate log integrity: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Close logger and perform cleanup"""
        # Could add cleanup operations here
        self.logger.info("Task logger closed")
    
    def __del__(self):
        """Destructor"""
        self.close()