# Microworkers Automation System 🤖

A complete autonomous AI agent system for performing Microworkers "Click + Search" tasks on Windows 10 using human-like behavior patterns to avoid bot detection.

## 🎯 Overview

This system provides a fully autonomous yet stealthy AI agent using n8n + MCP that:

- ✅ **Runs only "Click + Search" tasks** on Microworkers
- 🖱️ **Simulates human-like behavior** (mouse movement, scrolls, pauses)
- 🛡️ **Avoids bot detection triggers** (speed clicking, linear movements)
- 📸 **Captures screenshots** when requested
- 🚫 **NEVER attempts** video uploads, screen recordings, or mobile tasks
- 🔍 **Filters jobs** that are desktop-compatible only
- 💰 **Sorts tasks by highest payout** first
- ⏱️ **Waits 7–12 seconds between tasks** randomly (10-12 tasks per hour)
- 🎓 **Allows user training** for initial navigation and behavior
- 🔒 **NEVER clicks the "Remove" button** on job listings

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   n8n Workflow │ ←→ │  MCP Integration │ ←→ │ Python Automation│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Task Scheduling │    │   Validation     │    │ Human Behavior  │
│ & Coordination  │    │  & Monitoring    │    │   Simulation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the system files
cd microworkers-automation

# Install Python dependencies
pip install -r microworkers_requirements.txt

# Install Chrome browser (required for automation)
# Download from: https://www.google.com/chrome/
```

### 2. Initial Setup and Training

```bash
# Run system demonstration
python microworkers_main.py --mode=demo

# Enter training mode (REQUIRED for first use)
python microworkers_main.py --mode=train
```

### 3. Training Process

The training mode will guide you through:

1. **🖱️ Mouse Pattern Recording**
   - Record natural mouse movements
   - Learn curve patterns and timing
   - Capture human-like jitter and overshoots

2. **🎯 Click Target Training**
   - Mark elements to click (press 'c')
   - Mark elements to avoid (press 'r' - like Remove buttons)
   - Learn page layout and element recognition

3. **📄 Page Layout Learning**
   - Analyze Microworkers page structure
   - Save element positions and properties
   - Build navigation knowledge base

### 4. Validation and Testing

```bash
# Validate entire system
python microworkers_main.py --mode=validate
```

### 5. Run Automation

```bash
# Start autonomous automation
python microworkers_main.py --mode=run --username=YOUR_USERNAME --password=YOUR_PASSWORD

# Run for specific duration (4 hours max)
python microworkers_main.py --mode=run --username=USER --password=PASS --max-hours=4
```

## 🛠️ Configuration

### Environment Setup

Create a `.env` file for sensitive configuration:

```env
MW_USERNAME=your_microworkers_username
MW_PASSWORD=your_microworkers_password
LOG_LEVEL=INFO
SCREENSHOT_ENABLED=true
```

### Behavior Configuration

Edit `microworkers_config.py` to adjust:

```python
# Task filtering
TASK_FILTERS = {
    "categories": ["click_search", "search_click", "web_search"],
    "min_payout": 0.10,  # Minimum $0.10 per task
    "max_time_minutes": 15,
    "desktop_only": True,
    "exclude_mobile": True,
    "exclude_video": True
}

# Timing settings
TIMING_CONFIG = {
    "tasks_per_hour": {"min": 10, "max": 12},
    "between_tasks_delay": {"min": 7, "max": 12},  # seconds
    "click_delay": {"min": 1, "max": 2}
}

# Human-like behavior
MOUSE_CONFIG = {
    "movement_speed": {"min": 0.8, "max": 1.5},
    "curve_intensity": {"min": 0.3, "max": 0.7},
    "overshoot_probability": 0.15,
    "jitter_amount": {"min": 1, "max": 3}
}
```

## 🧠 Features

### Human-like Behavior Simulation

- **🌊 Bezier Curve Mouse Movement**: Natural curved paths instead of straight lines
- **🎯 Mouse Overshoots**: Occasional overshooting and correction like humans
- **📳 Random Jitter**: Small random movements during mouse travel
- **⏸️ Variable Timing**: Randomized delays between actions
- **📜 Smooth Scrolling**: Human-like scrolling patterns
- **✍️ Typing Simulation**: Natural typing with occasional typos and corrections

### Bot Detection Prevention

- **🕰️ Timing Randomization**: All actions use random timing within human ranges
- **📊 Success Rate Limiting**: Prevents suspiciously perfect performance
- **🔄 Pattern Variation**: Changes behavior patterns to avoid detection
- **📈 Rate Limiting**: Maintains 10-12 tasks per hour maximum
- **🛑 Validation Checks**: Continuous monitoring for bot-like behavior

### Task Management

- **🔍 Smart Filtering**: Only selects desktop-compatible Click + Search tasks
- **💰 Payout Optimization**: Sorts by highest payout first
- **📱 Mobile Exclusion**: Automatically excludes mobile-only tasks
- **🎥 Media Exclusion**: Avoids video upload/recording tasks
- **📸 Screenshot Handling**: Captures required screenshots

### Safety Features

- **🚫 Remove Button Protection**: Never clicks Remove buttons
- **⏱️ Time Limits**: Built-in session duration limits
- **🔄 Error Recovery**: Automatic error handling and recovery
- **📊 Performance Monitoring**: Tracks success rates and timing
- **🛡️ Validation Layer**: Multiple validation checkpoints

## 📁 Project Structure

```
microworkers-automation/
├── microworkers_main.py          # Main entry point
├── microworkers_config.py        # Configuration settings
├── microworkers_automation.py    # Core automation logic
├── human_automation.py           # Human behavior simulation
├── training_module.py            # User training interface
├── mcp_integration.py            # MCP protocol integration
├── microworkers_requirements.txt # Python dependencies
├── workflows/
│   └── microworkers_automation_workflow.json  # n8n workflow
├── training_data/                # User training data
│   ├── patterns/                 # Mouse patterns
│   ├── targets/                  # Click targets
│   └── layouts/                  # Page layouts
├── mw_screenshots/               # Screenshot storage
│   └── YYYY-MM-DD/              # Daily folders
├── logs/                         # System logs
└── config/                       # Configuration files
```

## 🔧 Advanced Usage

### n8n Workflow Integration

1. **Import Workflow**:
   ```bash
   # Import the n8n workflow
   n8n import:workflow workflows/microworkers_automation_workflow.json
   ```

2. **Configure Environment Variables** in n8n:
   - `MW_USERNAME`: Microworkers username
   - `MW_PASSWORD`: Microworkers password

3. **Activate Workflow**:
   - Set to run every 30 minutes
   - Monitor execution logs
   - Review automation performance

### MCP Integration Functions

The system provides these MCP functions for n8n:

```python
# Workflow initialization
start_here_workflow_guide()

# Node management
list_nodes(category='browser')
validate_node_minimal('browserMouse')
get_node_essentials('microworkersClickSearch')

# Validation
validate_node_operation()
validate_workflow_connections()
n8n_validate_workflow()

# Training
user_guided_training_mode()
```

### Custom Task Filters

Create custom task filtering logic:

```python
def custom_task_filter(task_title, task_description):
    """Custom task filtering logic"""
    
    # Add your custom criteria
    if "specific_keyword" in task_description.lower():
        return True
    
    # Check custom requirements
    if task_payout_meets_criteria(task_title):
        return True
    
    return False
```

## 📊 Monitoring and Logs

### Log Files

- **System Logs**: `logs/microworkers_YYYYMMDD_HHMMSS.log`
- **Session Stats**: Embedded in automation logs
- **Error Logs**: Detailed error information and stack traces

### Screenshots

- **Automatic Capture**: Screenshots saved for each task
- **Organized Storage**: Daily folders in `mw_screenshots/`
- **Validation Screenshots**: Before/after task completion

### Performance Monitoring

```python
# Get session statistics
stats = automation.get_session_stats()
print(f"Tasks completed: {stats['tasks_completed']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Session duration: {stats['session_duration_minutes']:.1f} minutes")
```

## ⚠️ Important Safety Guidelines

### ✅ DO's

- ✅ **Run training mode first** before automation
- ✅ **Monitor initial sessions** closely
- ✅ **Keep task rate** within 10-12 per hour
- ✅ **Use realistic delays** between actions
- ✅ **Check screenshots** for task validation
- ✅ **Keep logs** for performance analysis

### ❌ DON'Ts

- ❌ **Never run without training**
- ❌ **Don't exceed task rate limits**
- ❌ **Don't click Remove buttons**
- ❌ **Don't attempt video/mobile tasks**
- ❌ **Don't run 24/7 without breaks**
- ❌ **Don't ignore validation warnings**

### 🛡️ Bot Detection Prevention

The system includes multiple layers of bot detection prevention:

1. **Behavioral Randomization**: All timings and movements are randomized
2. **Human Pattern Simulation**: Based on recorded human interactions
3. **Success Rate Limiting**: Prevents perfect performance that seems robotic
4. **Rate Limiting**: Maintains human-like task completion rates
5. **Error Simulation**: Occasional failures to appear more human

## 🐛 Troubleshooting

### Common Issues

**Q: Login fails repeatedly**
```bash
# Check credentials and run validation
python microworkers_main.py --mode=validate
```

**Q: No tasks found**
- Verify task filters in `microworkers_config.py`
- Check if tasks are available on Microworkers
- Ensure desktop-compatible tasks exist

**Q: Mouse movements seem robotic**
- Retrain mouse patterns in training mode
- Adjust `MOUSE_CONFIG` parameters
- Increase randomization settings

**Q: Tasks fail validation**
- Review task filtering criteria
- Check screenshot requirements
- Verify task completion logic

### Debug Mode

```bash
# Run with debug logging
python microworkers_main.py --mode=run --log-level=DEBUG --username=USER --password=PASS
```

### Performance Issues

1. **Slow Performance**:
   - Reduce screenshot quality
   - Optimize mouse movement speed
   - Check system resources

2. **High Failure Rate**:
   - Retrain click targets
   - Adjust timing settings
   - Review task filtering

## 📝 License and Disclaimer

**EDUCATIONAL USE ONLY**: This system is provided for educational and research purposes. Users are responsible for compliance with Microworkers terms of service and applicable laws.

**NO WARRANTY**: This software is provided "as is" without warranty of any kind.

**USER RESPONSIBILITY**: Users must ensure their use complies with all applicable terms of service and legal requirements.

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Test thoroughly**: Ensure all validations pass
4. **Submit pull request**: Include detailed description

## 📞 Support

For issues and questions:

1. **Check troubleshooting section** above
2. **Review log files** for error details
3. **Run validation mode** to identify issues
4. **Create issue** with detailed information

---

**🎯 Remember**: This system prioritizes **stealth and human-like behavior** over speed. The goal is sustainable, undetectable automation that provides value while respecting platform guidelines.