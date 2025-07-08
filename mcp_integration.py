import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from microworkers_automation import MicroworkersAutomation
from training_module import user_guided_training_mode, start_here_workflow_guide
from human_automation import HumanBrowserAutomation
from microworkers_config import config

logger = logging.getLogger(__name__)

@dataclass
class MCPNode:
    """Represents an MCP node with its properties and validation"""
    
    id: str
    name: str
    category: str
    description: str
    parameters: Dict[str, Any]
    validation_rules: Dict[str, Any]
    is_validated: bool = False

class MCPNodeRegistry:
    """Registry for MCP nodes used in Microworkers automation"""
    
    def __init__(self):
        self.nodes = {}
        self.initialize_default_nodes()
    
    def initialize_default_nodes(self) -> None:
        """Initialize default MCP nodes for Microworkers automation"""
        
        # Browser automation nodes
        self.register_node(MCPNode(
            id="browserMouse",
            name="Browser Mouse Control",
            category="browser",
            description="Human-like mouse movement and clicking for browser automation",
            parameters={
                "movement_type": "bezier_curve",
                "jitter_enabled": True,
                "overshoot_probability": 0.15,
                "pause_enabled": True
            },
            validation_rules={
                "bot_detection_check": True,
                "timing_validation": True,
                "pattern_analysis": True
            }
        ))
        
        self.register_node(MCPNode(
            id="microworkersClickSearch",
            name="Microworkers Click+Search Handler",
            category="microworkers",
            description="Core logic for handling Click + Search tasks on Microworkers",
            parameters={
                "task_filters": config.TASK_FILTERS,
                "timing_config": config.TIMING_CONFIG,
                "payout_sorting": "highest_first",
                "max_tasks_per_cycle": 3
            },
            validation_rules={
                "task_validation": True,
                "filter_compliance": True,
                "rate_limiting": True,
                "success_tracking": True
            }
        ))
        
        # Validation nodes
        self.register_node(MCPNode(
            id="behaviorValidator",
            name="Human Behavior Validator",
            category="validation",
            description="Validates automation behavior to ensure human-like patterns",
            parameters={
                "timing_checks": True,
                "success_rate_analysis": True,
                "pattern_detection": True,
                "bot_prevention": True
            },
            validation_rules={
                "validation_threshold": 0.85,
                "timing_tolerance": 0.2,
                "max_success_rate": 95
            }
        ))
        
        # Training nodes
        self.register_node(MCPNode(
            id="trainingRecorder",
            name="Training Pattern Recorder",
            category="training",
            description="Records user patterns for training the automation system",
            parameters={
                "record_mouse": True,
                "record_clicks": True,
                "record_timing": True,
                "save_patterns": True
            },
            validation_rules={
                "min_samples": 5,
                "pattern_quality": 0.8
            }
        ))
    
    def register_node(self, node: MCPNode) -> None:
        """Register a new MCP node"""
        self.nodes[node.id] = node
        logger.info(f"Registered MCP node: {node.id}")
    
    def get_node(self, node_id: str) -> Optional[MCPNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def list_nodes(self, category: str = None) -> List[MCPNode]:
        """List nodes, optionally filtered by category"""
        if category:
            return [node for node in self.nodes.values() if node.category == category]
        return list(self.nodes.values())

class MCPWorkflowValidator:
    """Validates MCP workflow operations"""
    
    def __init__(self, node_registry: MCPNodeRegistry):
        self.node_registry = node_registry
        self.validation_history = []
    
    def validate_node_minimal(self, node_id: str) -> Dict[str, Any]:
        """Minimal validation for a specific node"""
        node = self.node_registry.get_node(node_id)
        
        if not node:
            return {
                "status": "error",
                "message": f"Node {node_id} not found",
                "validation_passed": False
            }
        
        validation_results = {
            "node_id": node_id,
            "node_name": node.name,
            "category": node.category,
            "validation_passed": True,
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Perform specific validations based on node type
        if node_id == "browserMouse":
            validation_results["checks"] = self._validate_browser_mouse_node(node)
        elif node_id == "microworkersClickSearch":
            validation_results["checks"] = self._validate_microworkers_node(node)
        elif node_id == "behaviorValidator":
            validation_results["checks"] = self._validate_behavior_validator_node(node)
        
        # Check if all validations passed
        validation_results["validation_passed"] = all(
            check.get("passed", False) for check in validation_results["checks"].values()
        )
        
        node.is_validated = validation_results["validation_passed"]
        self.validation_history.append(validation_results)
        
        return validation_results
    
    def _validate_browser_mouse_node(self, node: MCPNode) -> Dict[str, Any]:
        """Validate browser mouse node"""
        checks = {}
        
        # Check bot detection prevention
        checks["bot_detection"] = {
            "description": "Bot detection prevention measures",
            "passed": (
                node.parameters.get("jitter_enabled", False) and
                node.parameters.get("overshoot_probability", 0) > 0 and
                node.parameters.get("movement_type") == "bezier_curve"
            ),
            "details": "Human-like movement patterns configured"
        }
        
        # Check timing validation
        checks["timing_validation"] = {
            "description": "Timing appears human-like",
            "passed": node.parameters.get("pause_enabled", False),
            "details": "Random pauses enabled for natural behavior"
        }
        
        return checks
    
    def _validate_microworkers_node(self, node: MCPNode) -> Dict[str, Any]:
        """Validate Microworkers-specific node"""
        checks = {}
        
        # Check task filtering
        task_filters = node.parameters.get("task_filters", {})
        checks["task_filtering"] = {
            "description": "Task filtering rules are properly configured",
            "passed": (
                task_filters.get("desktop_only", False) and
                task_filters.get("exclude_mobile", False) and
                task_filters.get("exclude_video", False)
            ),
            "details": "Desktop-only, Click+Search tasks filtered correctly"
        }
        
        # Check rate limiting
        timing_config = node.parameters.get("timing_config", {})
        checks["rate_limiting"] = {
            "description": "Rate limiting prevents suspicious behavior",
            "passed": (
                timing_config.get("tasks_per_hour", {}).get("max", 999) <= 12 and
                timing_config.get("between_tasks_delay", {}).get("min", 0) >= 7
            ),
            "details": "Task rate limited to 10-12 per hour with 7-12 second delays"
        }
        
        # Check payout sorting
        checks["payout_optimization"] = {
            "description": "Tasks sorted by highest payout first",
            "passed": node.parameters.get("payout_sorting") == "highest_first",
            "details": "Payout optimization enabled"
        }
        
        return checks
    
    def _validate_behavior_validator_node(self, node: MCPNode) -> Dict[str, Any]:
        """Validate behavior validator node"""
        checks = {}
        
        # Check validation thresholds
        validation_rules = node.validation_rules
        checks["validation_threshold"] = {
            "description": "Validation threshold is reasonable",
            "passed": 0.7 <= validation_rules.get("validation_threshold", 0) <= 0.9,
            "details": "Threshold allows for natural human variation"
        }
        
        # Check success rate limits
        checks["success_rate_check"] = {
            "description": "Success rate limits prevent bot detection",
            "passed": validation_rules.get("max_success_rate", 100) < 100,
            "details": "Maximum success rate prevents suspiciously perfect performance"
        }
        
        return checks
    
    def validate_node_operation(self, node_id: str, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific node operation"""
        node = self.node_registry.get_node(node_id)
        
        if not node:
            return {
                "status": "error",
                "message": f"Node {node_id} not found"
            }
        
        # Validate operation based on node type
        if node_id == "microworkersClickSearch":
            return self._validate_microworkers_operation(operation_data)
        elif node_id == "browserMouse":
            return self._validate_browser_operation(operation_data)
        
        return {"status": "success", "message": "Operation validated"}
    
    def _validate_microworkers_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Microworkers operation data"""
        validations = {
            "job_parsing": {
                "passed": "tasks" in operation_data,
                "message": "Task data present"
            },
            "link_selection": {
                "passed": all(
                    task.get("is_valid", False) for task in operation_data.get("tasks", [])
                ),
                "message": "All selected tasks are valid"
            },
            "success_ratio": {
                "passed": True,  # Will be checked during execution
                "message": "Success ratio monitoring enabled"
            },
            "filter_conditions": {
                "passed": all(
                    task.get("desktop_compatible", False) and 
                    not any(exclude in task.get("description", "").lower() 
                           for exclude in ["video", "mobile", "record"])
                    for task in operation_data.get("tasks", [])
                ),
                "message": "Filter conditions applied correctly"
            }
        }
        
        all_passed = all(v["passed"] for v in validations.values())
        
        return {
            "status": "success" if all_passed else "warning",
            "validations": validations,
            "overall_passed": all_passed
        }
    
    def _validate_browser_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate browser operation data"""
        validations = {
            "human_timing": {
                "passed": operation_data.get("timing_randomized", False),
                "message": "Timing randomization applied"
            },
            "mouse_patterns": {
                "passed": operation_data.get("curve_movement", False),
                "message": "Curved mouse movements used"
            },
            "click_patterns": {
                "passed": operation_data.get("click_delay", 0) > 0,
                "message": "Click delays applied"
            }
        }
        
        all_passed = all(v["passed"] for v in validations.values())
        
        return {
            "status": "success" if all_passed else "warning",
            "validations": validations,
            "overall_passed": all_passed
        }

class MCPWorkflowManager:
    """Manages MCP workflow connections and validation"""
    
    def __init__(self):
        self.node_registry = MCPNodeRegistry()
        self.validator = MCPWorkflowValidator(self.node_registry)
        self.automation_instance = None
    
    def get_node_essentials(self, node_id: str) -> Dict[str, Any]:
        """Get essential information about a node"""
        node = self.node_registry.get_node(node_id)
        
        if not node:
            return {
                "status": "error",
                "message": f"Node {node_id} not found"
            }
        
        return {
            "status": "success",
            "node_id": node.id,
            "name": node.name,
            "category": node.category,
            "description": node.description,
            "parameters": node.parameters,
            "validation_rules": node.validation_rules,
            "is_validated": node.is_validated
        }
    
    def validate_workflow_connections(self) -> Dict[str, Any]:
        """Validate all workflow connections"""
        validation_results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "node_validations": {},
            "overall_status": "passed"
        }
        
        # Validate each node
        for node_id in self.node_registry.nodes.keys():
            node_validation = self.validator.validate_node_minimal(node_id)
            validation_results["node_validations"][node_id] = node_validation
            
            if not node_validation["validation_passed"]:
                validation_results["overall_status"] = "failed"
        
        # Check workflow connectivity
        connectivity_check = self._check_workflow_connectivity()
        validation_results["connectivity"] = connectivity_check
        
        if not connectivity_check["passed"]:
            validation_results["overall_status"] = "failed"
        
        return validation_results
    
    def _check_workflow_connectivity(self) -> Dict[str, Any]:
        """Check if workflow nodes are properly connected"""
        required_nodes = ["browserMouse", "microworkersClickSearch", "behaviorValidator"]
        missing_nodes = []
        
        for node_id in required_nodes:
            if node_id not in self.node_registry.nodes:
                missing_nodes.append(node_id)
        
        return {
            "passed": len(missing_nodes) == 0,
            "message": "All required nodes present" if len(missing_nodes) == 0 else f"Missing nodes: {missing_nodes}",
            "required_nodes": required_nodes,
            "missing_nodes": missing_nodes
        }
    
    def n8n_validate_workflow(self) -> Dict[str, Any]:
        """Final validation before deploying n8n workflow"""
        workflow_validation = self.validate_workflow_connections()
        
        # Additional deployment checks
        deployment_checks = {
            "credentials_configured": self._check_credentials(),
            "dependencies_installed": self._check_dependencies(),
            "training_data_available": self._check_training_data(),
            "screenshot_directory": self._check_screenshot_directory()
        }
        
        all_deployment_checks = all(deployment_checks.values())
        
        return {
            "status": "ready" if workflow_validation["overall_status"] == "passed" and all_deployment_checks else "not_ready",
            "workflow_validation": workflow_validation,
            "deployment_checks": deployment_checks,
            "ready_for_deployment": workflow_validation["overall_status"] == "passed" and all_deployment_checks,
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_credentials(self) -> bool:
        """Check if Microworkers credentials are configured"""
        # This would check environment variables or config files
        # For now, return True (implement based on your credential system)
        return True
    
    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        try:
            import selenium
            import pyautogui
            import cv2
            import PIL
            return True
        except ImportError:
            return False
    
    def _check_training_data(self) -> bool:
        """Check if training data is available"""
        training_dir = Path("./training_data")
        return training_dir.exists() and any(training_dir.iterdir())
    
    def _check_screenshot_directory(self) -> bool:
        """Check if screenshot directory can be created"""
        try:
            screenshot_dir = Path(config.SCREENSHOT_CONFIG["save_directory"])
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

# Main MCP integration functions
mcp_manager = MCPWorkflowManager()

def list_nodes(category: str = None) -> List[Dict[str, Any]]:
    """List all available MCP nodes"""
    nodes = mcp_manager.node_registry.list_nodes(category)
    return [
        {
            "id": node.id,
            "name": node.name,
            "category": node.category,
            "description": node.description,
            "is_validated": node.is_validated
        }
        for node in nodes
    ]

def validate_node_minimal(node_id: str) -> Dict[str, Any]:
    """Perform minimal validation on a specific node"""
    return mcp_manager.validator.validate_node_minimal(node_id)

def get_node_essentials(node_id: str) -> Dict[str, Any]:
    """Get essential information about a node"""
    return mcp_manager.get_node_essentials(node_id)

def validate_node_operation(node_id: str, operation_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validate a specific node operation"""
    if operation_data is None:
        operation_data = {}
    return mcp_manager.validator.validate_node_operation(node_id, operation_data)

def validate_workflow_connections() -> Dict[str, Any]:
    """Validate all workflow connections"""
    return mcp_manager.validate_workflow_connections()

def n8n_validate_workflow() -> Dict[str, Any]:
    """Final validation before deploying n8n workflow"""
    return mcp_manager.n8n_validate_workflow()

# Export main functions for n8n integration
__all__ = [
    'start_here_workflow_guide',
    'list_nodes',
    'validate_node_minimal',
    'get_node_essentials',
    'validate_node_operation',
    'validate_workflow_connections',
    'n8n_validate_workflow',
    'user_guided_training_mode'
]