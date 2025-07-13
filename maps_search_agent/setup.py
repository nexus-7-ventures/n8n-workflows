#!/usr/bin/env python3
"""
Setup script for Maps Search Evaluation Agent
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python packages")
        return False

def check_guidelines():
    """Check if guidelines.txt exists"""
    guidelines_path = Path("guidelines.txt")
    if guidelines_path.exists():
        print("✅ guidelines.txt found")
        return True
    else:
        print("❌ guidelines.txt NOT FOUND")
        print("   Please add your June 2024 Maps Search Guidelines file as 'guidelines.txt'")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        subprocess.check_output(["tesseract", "--version"], stderr=subprocess.STDOUT)
        print("✅ Tesseract OCR found")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tesseract OCR not found")
        print("   Please install Tesseract OCR from:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def main():
    """Main setup function"""
    print("🚀 Maps Search Evaluation Agent Setup")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 4
    
    # Check Python version
    if check_python_version():
        checks_passed += 1
    
    # Check guidelines file
    if check_guidelines():
        checks_passed += 1
    
    # Install requirements
    if install_requirements():
        checks_passed += 1
    
    # Check Tesseract
    if check_tesseract():
        checks_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Setup Complete: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("✅ All checks passed! Ready to run the agent.")
        print("   Run: python main.py")
    else:
        print("❌ Please fix the issues above before running the agent.")
    
    return checks_passed == total_checks

if __name__ == "__main__":
    main()
