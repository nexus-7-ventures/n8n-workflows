#!/usr/bin/env python3
"""
Microworkers Automation Main Entry Point

This script provides the main interface for running the Microworkers
Click + Search automation system with n8n + MCP integration.

Features:
- Complete autonomous task execution
- Human-like behavior simulation
- Training mode for initial setup
- Comprehensive logging and validation
- Bot detection prevention
"""

import sys
import os
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from microworkers_automation import MicroworkersAutomation
from training_module import user_guided_training_mode, start_here_workflow_guide
from mcp_integration import (
    list_nodes, validate_node_minimal, get_node_essentials,
    validate_node_operation, validate_workflow_connections,
    n8n_validate_workflow
)
from microworkers_config import config, config_manager

# Set up logging
def setup_logging(level: str = "INFO") -> None:
    """Set up comprehensive logging system"""
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # Main log file
    log_filename = log_dir / f"microworkers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Log file: {log_filename}")

class MicroworkersController:
    """Main controller for Microworkers automation system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.automation = None
        self.session_active = False
    
    def run_training_mode(self) -> None:
        """Run the training mode for initial setup"""
        self.logger.info("Starting Microworkers training mode...")
        
        print("\n" + "="*60)
        print("MICROWORKERS AUTOMATION - TRAINING MODE")
        print("="*60)
        print()
        print("This will guide you through setting up the automation:")
        print("1. Record human-like mouse patterns")
        print("2. Train click target recognition")
        print("3. Learn page layouts")
        print("4. Configure behavior parameters")
        print()
        
        try:
            user_guided_training_mode()
            self.logger.info("Training mode completed successfully")
        except Exception as e:
            self.logger.error(f"Training mode failed: {e}")
            raise
    
    def validate_system(self) -> bool:
        """Validate the entire system before running"""
        self.logger.info("Validating Microworkers automation system...")
        
        print("Validating system components...")
        
        # Validate workflow connections
        workflow_validation = validate_workflow_connections()
        
        if workflow_validation["overall_status"] != "passed":
            self.logger.error("Workflow validation failed")
            print("❌ Workflow validation failed:")
            for node_id, validation in workflow_validation["node_validations"].items():
                if not validation["validation_passed"]:
                    print(f"  - {node_id}: {validation.get('message', 'Unknown error')}")
            return False
        
        # Final n8n workflow validation
        n8n_validation = n8n_validate_workflow()
        
        if not n8n_validation["ready_for_deployment"]:
            self.logger.error("n8n workflow validation failed")
            print("❌ n8n workflow validation failed:")
            for check, passed in n8n_validation["deployment_checks"].items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}")
            return False
        
        print("✅ All system validations passed!")
        self.logger.info("System validation completed successfully")
        return True
    
    def run_automation_session(self, username: str, password: str, max_duration_hours: int = 8) -> Dict[str, Any]:
        """Run a complete automation session"""
        self.logger.info(f"Starting Microworkers automation session (max duration: {max_duration_hours}h)")
        
        if not username or not password:
            raise ValueError("Username and password are required")
        
        try:
            # Initialize automation
            self.automation = MicroworkersAutomation()
            self.session_active = True
            
            # Login
            print("Logging in to Microworkers...")
            login_success = self.automation.login(username, password)
            
            if not login_success:
                raise Exception("Failed to login to Microworkers")
            
            print("✅ Login successful!")
            
            # Run automation cycles
            session_results = {
                "session_start": datetime.now().isoformat(),
                "cycles_completed": 0,
                "total_tasks_completed": 0,
                "total_tasks_failed": 0,
                "session_duration_minutes": 0,
                "success_rate": 0
            }
            
            cycle_count = 0
            max_cycles = max_duration_hours * 2  # 2 cycles per hour (30 min intervals)
            
            while self.session_active and cycle_count < max_cycles:
                cycle_count += 1
                self.logger.info(f"Starting automation cycle {cycle_count}")
                
                print(f"\n--- Automation Cycle {cycle_count} ---")
                
                try:
                    # Run one automation cycle
                    self.automation.run_automation_cycle()
                    
                    # Get updated stats
                    stats = self.automation.get_session_stats()
                    
                    session_results.update({
                        "cycles_completed": cycle_count,
                        "total_tasks_completed": stats["tasks_completed"],
                        "total_tasks_failed": stats["tasks_failed"],
                        "session_duration_minutes": stats["session_duration_minutes"],
                        "success_rate": stats["success_rate"]
                    })
                    
                    print(f"Cycle {cycle_count} completed:")
                    print(f"  Tasks completed this session: {stats['tasks_completed']}")
                    print(f"  Success rate: {stats['success_rate']:.1f}%")
                    print(f"  Session duration: {stats['session_duration_minutes']:.1f} minutes")
                    
                    # Check if we should continue
                    if not self.automation.should_continue_session():
                        self.logger.info("Session time limit reached")
                        break
                    
                except Exception as e:
                    self.logger.error(f"Error in automation cycle {cycle_count}: {e}")
                    print(f"❌ Error in cycle {cycle_count}: {e}")
                    
                    # Continue with next cycle unless it's a critical error
                    if "login" in str(e).lower() or "connection" in str(e).lower():
                        break
            
            session_results["session_end"] = datetime.now().isoformat()
            
            print(f"\n✅ Automation session completed!")
            print(f"Total cycles: {session_results['cycles_completed']}")
            print(f"Total tasks completed: {session_results['total_tasks_completed']}")
            print(f"Final success rate: {session_results['success_rate']:.1f}%")
            
            self.logger.info("Automation session completed successfully")
            return session_results
            
        except Exception as e:
            self.logger.error(f"Automation session failed: {e}")
            raise
        finally:
            self.cleanup()
    
    def run_demo_mode(self) -> None:
        """Run a demonstration of the system capabilities"""
        self.logger.info("Starting demo mode...")
        
        print("\n" + "="*60)
        print("MICROWORKERS AUTOMATION - DEMO MODE")
        print("="*60)
        print()
        
        # Demo workflow validation
        print("1. Validating MCP nodes...")
        browser_nodes = list_nodes(category="browser")
        print(f"   Found {len(browser_nodes)} browser automation nodes")
        
        microworkers_nodes = list_nodes(category="microworkers")
        print(f"   Found {len(microworkers_nodes)} Microworkers-specific nodes")
        
        # Demo node validation
        print("\n2. Validating critical nodes...")
        critical_nodes = ["browserMouse", "microworkersClickSearch", "behaviorValidator"]
        
        for node_id in critical_nodes:
            validation = validate_node_minimal(node_id)
            status = "✅" if validation["validation_passed"] else "❌"
            print(f"   {status} {node_id}: {validation.get('message', 'OK')}")
        
        # Demo workflow connections
        print("\n3. Checking workflow connections...")
        workflow_check = validate_workflow_connections()
        connectivity_status = "✅" if workflow_check["connectivity"]["passed"] else "❌"
        print(f"   {connectivity_status} Workflow connectivity: {workflow_check['connectivity']['message']}")
        
        # Demo configuration
        print("\n4. Configuration overview:")
        print(f"   Max tasks per hour: {config.TIMING_CONFIG['tasks_per_hour']['max']}")
        print(f"   Task delay range: {config.TIMING_CONFIG['between_tasks_delay']['min']}-{config.TIMING_CONFIG['between_tasks_delay']['max']} seconds")
        print(f"   Screenshot directory: {config.SCREENSHOT_CONFIG['save_directory']}")
        print(f"   Human-like mouse movements: Enabled")
        print(f"   Bot detection prevention: Enabled")
        
        print("\n5. System status:")
        final_validation = n8n_validate_workflow()
        if final_validation["ready_for_deployment"]:
            print("   ✅ System ready for deployment")
        else:
            print("   ❌ System needs configuration")
            
        print("\nDemo completed! Use --mode=train to set up the system or --mode=run to start automation.")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.session_active = False
        if self.automation:
            try:
                self.automation.cleanup()
            except Exception as e:
                self.logger.warning(f"Cleanup warning: {e}")
        
        self.logger.info("System cleanup completed")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Microworkers Click+Search Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode=demo                           # Run system demonstration
  %(prog)s --mode=train                          # Enter training mode
  %(prog)s --mode=validate                       # Validate system components
  %(prog)s --mode=run --username=USER --password=PASS  # Run automation
  %(prog)s --mode=run --max-hours=4              # Run for 4 hours max
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["demo", "train", "validate", "run"],
        default="demo",
        help="Operation mode (default: demo)"
    )
    
    parser.add_argument(
        "--username",
        help="Microworkers username"
    )
    
    parser.add_argument(
        "--password",
        help="Microworkers password"
    )
    
    parser.add_argument(
        "--max-hours",
        type=int,
        default=8,
        help="Maximum session duration in hours (default: 8)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Print header
    print("="*60)
    print("MICROWORKERS AUTOMATION SYSTEM")
    print("Autonomous Click + Search Task Execution")
    print("="*60)
    
    try:
        controller = MicroworkersController()
        
        if args.mode == "demo":
            controller.run_demo_mode()
            
        elif args.mode == "train":
            controller.run_training_mode()
            
        elif args.mode == "validate":
            if controller.validate_system():
                print("✅ System validation passed!")
            else:
                print("❌ System validation failed!")
                sys.exit(1)
                
        elif args.mode == "run":
            if not args.username or not args.password:
                print("❌ Username and password required for run mode")
                print("Use: python microworkers_main.py --mode=run --username=YOUR_USER --password=YOUR_PASS")
                sys.exit(1)
            
            # Validate system first
            if not controller.validate_system():
                print("❌ System validation failed. Use --mode=train first.")
                sys.exit(1)
            
            # Run automation
            results = controller.run_automation_session(
                username=args.username,
                password=args.password,
                max_duration_hours=args.max_hours
            )
            
            print(f"\nSession Summary:")
            print(f"Duration: {results['session_duration_minutes']:.1f} minutes")
            print(f"Tasks completed: {results['total_tasks_completed']}")
            print(f"Success rate: {results['success_rate']:.1f}%")
    
    except KeyboardInterrupt:
        logger.info("User interrupted execution")
        print("\n⚠️  Execution interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()