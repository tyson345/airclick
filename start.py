#!/usr/bin/env python3
"""
Gesture Control Hub - Startup Script
This script launches the main Flask application and provides setup instructions.
"""

import subprocess
import sys
import time
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'opencv-python', 'mediapipe', 'numpy', 
        'pyautogui', 'pynput', 'websockets'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed!")
    return True

def main():
    print("🚀 Gesture Control Hub - Starting Up...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n📋 Available Features:")
    print("   • Regular Mode - Mouse control")
    print("   • Movie Mode - Media playback")
    print("   • Game Mode - Gaming precision")
    print("   • Presentation Mode - Public speaking")
    print("   • Camera Mode - Photo/video capture")
    print("   • AI Server Management - WebSocket server control")
    
    print("\n🌐 Starting Flask application...")
    print("   Web interface will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop the application")
    print("\n" + "=" * 50)
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 