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
    # Map package names to their import names
    package_imports = {
        'flask': 'flask',
        'opencv-python': 'cv2', 
        'mediapipe': 'mediapipe',
        'numpy': 'numpy',
        'pyautogui': 'pyautogui',
        'pynput': 'pynput',
        'websockets': 'websockets'
    }
    
    missing_packages = []
    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        print("\n💡 Or install individually:")
        for package in missing_packages:
            print(f"   pip install {package}")
        return False
    
    print("✅ All required packages are installed!")
    return True

def check_mode_files():
    """Check which mode files exist"""
    mode_files = [
        'regular.py',
        'movie.py', 
        'game.py',
        'presentation.py',
        'camera.py',
        'hand_detection_server.py'
    ]
    
    existing_files = []
    missing_files = []
    
    for file in mode_files:
        if os.path.exists(file):
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    print(f"\n📁 Mode Files Status:")
    if existing_files:
        print("   ✅ Available modes:")
        for file in existing_files:
            mode_name = file.replace('.py', '').replace('_', ' ').title()
            print(f"      - {mode_name} ({file})")
    
    if missing_files:
        print("   ⚠️  Missing mode files (these modes will be disabled):")
        for file in missing_files:
            mode_name = file.replace('.py', '').replace('_', ' ').title()
            print(f"      - {mode_name} ({file})")
        print("\n   💡 Note: Voice Assistant and Voice Notes work without additional files")
    
    return len(existing_files) > 0 or True  # Always return True since voice modes work

def main():
    print("🚀 Gesture Control Hub - Starting Up...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before continuing.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check mode files
    check_mode_files()
    
    print("\n📋 Available Features:")
    print("   • Voice Assistant - AI-powered voice commands (always available)")
    print("   • Voice Notes - Voice-to-text note taking (always available)")
    print("   • Regular Mode - Mouse control (requires regular.py)")
    print("   • Movie Mode - Media playback (requires movie.py)")
    print("   • Game Mode - Gaming precision (requires game.py)")
    print("   • Presentation Mode - Public speaking (requires presentation.py)")
    print("   • Camera Mode - Photo/video capture (requires camera.py)")
    print("   • AI Server Management - WebSocket server (requires hand_detection_server.py)")
    
    print("\n🌐 Starting Flask application...")
    print("   Web interface will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop the application")
    print("\n" + "=" * 50)
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except FileNotFoundError:
        print("\n❌ Error: app.py not found in current directory")
        print("   Make sure you're running this script from the correct folder")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
