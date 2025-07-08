#!/usr/bin/env python3
"""
Microworkers Automation System Setup Script

This script automates the setup and configuration of the complete
Microworkers automation system.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print setup header"""
    print("="*60)
    print("MICROWORKERS AUTOMATION SYSTEM SETUP")
    print("="*60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def check_system_requirements():
    """Check system requirements"""
    print("\n🖥️  Checking system requirements...")
    
    system = platform.system()
    print(f"   Operating System: {system}")
    
    if system == "Windows":
        if platform.release() == "10":
            print("✅ Windows 10 - Optimal")
        else:
            print("⚠️  Windows 10 recommended for best compatibility")
    else:
        print("⚠️  System designed for Windows 10, may need adjustments")
    
    return True

def create_directory_structure():
    """Create required directory structure"""
    print("\n📁 Creating directory structure...")
    
    directories = [
        "config",
        "logs",
        "mw_screenshots",
        "training_data/patterns",
        "training_data/targets",
        "training_data/layouts",
        "training_data/feedback"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    requirements_file = "microworkers_requirements.txt"
    
    if not Path(requirements_file).exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        print("   Installing packages (this may take a few minutes)...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_chrome_installation():
    """Check if Chrome is installed"""
    print("\n🌐 Checking Chrome installation...")
    
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "/usr/bin/google-chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    ]
    
    for path in chrome_paths:
        if Path(path).exists():
            print("✅ Chrome browser found")
            return True
    
    print("⚠️  Chrome browser not found")
    print("   Please install Chrome from: https://www.google.com/chrome/")
    return False

def setup_environment_file():
    """Create environment configuration file"""
    print("\n⚙️  Setting up environment configuration...")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ Environment file already exists")
        return True
    
    env_content = """# Microworkers Automation Environment Configuration
# Add your Microworkers credentials here

MW_USERNAME=your_microworkers_username
MW_PASSWORD=your_microworkers_password

# System Configuration
LOG_LEVEL=INFO
SCREENSHOT_ENABLED=true
DEBUG_MODE=false

# Timing Configuration (adjust if needed)
MAX_TASKS_PER_HOUR=12
MIN_TASK_DELAY=7
MAX_TASK_DELAY=12

# Browser Configuration
BROWSER_HEADLESS=false
BROWSER_WIDTH=1366
BROWSER_HEIGHT=768
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created (.env)")
    print("   📝 Please edit .env file with your Microworkers credentials")
    return True

def create_sample_config():
    """Create sample configuration files"""
    print("\n📋 Creating sample configuration...")
    
    config_dir = Path("config")
    
    # Create sample config file
    sample_config = config_dir / "sample_config.json"
    config_content = {
        "task_filters": {
            "min_payout": 0.10,
            "max_time_minutes": 15,
            "categories": ["click_search", "search_click", "web_search"]
        },
        "timing": {
            "tasks_per_hour_max": 12,
            "between_tasks_delay_min": 7,
            "between_tasks_delay_max": 12
        },
        "behavior": {
            "mouse_movement_speed": [0.8, 1.5],
            "jitter_enabled": True,
            "overshoot_probability": 0.15
        }
    }
    
    import json
    with open(sample_config, 'w') as f:
        json.dump(config_content, f, indent=2)
    
    print("✅ Sample configuration created")
    return True

def run_system_validation():
    """Run initial system validation"""
    print("\n🔍 Running system validation...")
    
    try:
        # Import and test main modules
        sys.path.insert(0, os.getcwd())
        
        print("   Testing configuration module...")
        import microworkers_config
        print("   ✅ Configuration module loaded")
        
        print("   Testing MCP integration...")
        import mcp_integration
        print("   ✅ MCP integration loaded")
        
        print("   Testing automation modules...")
        import human_automation
        print("   ✅ Human automation module loaded")
        
        print("✅ System validation passed")
        return True
        
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def show_next_steps():
    """Show next steps to user"""
    print("\n🎯 Next Steps:")
    print()
    print("1. 📝 Edit the .env file with your Microworkers credentials:")
    print("   MW_USERNAME=your_actual_username")
    print("   MW_PASSWORD=your_actual_password")
    print()
    print("2. 🎓 Run training mode (REQUIRED before automation):")
    print("   python microworkers_main.py --mode=train")
    print()
    print("3. 🔍 Validate the system:")
    print("   python microworkers_main.py --mode=validate")
    print()
    print("4. 🚀 Run the automation:")
    print("   python microworkers_main.py --mode=run --username=USER --password=PASS")
    print()
    print("5. 📖 Read the full documentation:")
    print("   Open MICROWORKERS_README.md for detailed instructions")
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_system_requirements():
        print("⚠️  Continuing with setup despite system warnings...")
    
    # Setup steps
    steps = [
        ("Creating directories", create_directory_structure),
        ("Installing dependencies", install_dependencies),
        ("Checking Chrome", check_chrome_installation),
        ("Setting up environment", setup_environment_file),
        ("Creating configuration", create_sample_config),
        ("Validating system", run_system_validation)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    if failed_steps:
        print("⚠️  Setup completed with some issues:")
        for step in failed_steps:
            print(f"   ❌ {step}")
        print()
        print("Please resolve the issues above before proceeding.")
    else:
        print("✅ Setup completed successfully!")
        print()
        show_next_steps()
    
    print("="*60)

if __name__ == "__main__":
    main()