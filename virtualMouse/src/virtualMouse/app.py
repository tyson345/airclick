import toga
import toga.style
import threading
import time
import sys
import os
import socket
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root (parent of virtualMouse) to sys.path BEFORE importing project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

imported_modules = {}

def lazy_import(module_name):
    """Lazy import modules to prevent immediate initialization"""
    if module_name not in imported_modules:
        try:
            imported_modules[module_name] = __import__(module_name)
            logger.info(f"Successfully imported {module_name}")
        except ImportError as e:
            logger.warning(f"Module {module_name} not available: {e}")
            imported_modules[module_name] = None
    return imported_modules[module_name]

try:
    from app import app   # Now it should find the main app.py
    logger.info("Successfully imported Flask app")
except ImportError as e:
    logger.error(f"Failed to import Flask app: {e}")
    # Create a minimal Flask app as fallback
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "<h1>AirClick - Virtual Mouse</h1><p>Welcome! Click on different modes to get started.</p>"


def run_flask():
    """Run Flask inside a thread"""
    try:
        logger.info("Starting Flask server...")
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")


def wait_for_flask(host="127.0.0.1", port=5000, timeout=30):
    """Wait until Flask server is ready or timeout"""
    logger.info(f"Waiting for Flask server at {host}:{port}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                logger.info("Flask server is ready!")
                return True
        except OSError:
            time.sleep(0.5)
    logger.error("Flask server did not start in time.")
    return False


class AirClick(toga.App):
    def startup(self):
        logger.info("Starting AirClick application...")
        
        try:
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            logger.info("Flask thread started")
        except Exception as e:
            logger.error(f"Failed to start Flask thread: {e}")

        # Wait until Flask server is ready
        if wait_for_flask():
            logger.info("✅ Flask server is up!")
        else:
            logger.error("❌ Flask server did not start in time.")

        try:
            self.main_window = toga.MainWindow(title="AirClick - Virtual Mouse")
            
            try:
                web = toga.WebView(url="http://127.0.0.1:5000")
                self.main_window.content = web
                logger.info("WebView created successfully")
            except Exception as e:
                logger.error(f"Failed to create WebView: {e}")
                # Create a simple error message box as fallback
                error_box = toga.Box(
                    children=[
                        toga.Label("AirClick - Error", style=toga.style.Pack(text_align="center", padding=10)),
                        toga.Label("Failed to load camera interface.", style=toga.style.Pack(text_align="center", padding=5)),
                        toga.Label("Please check camera permissions.", style=toga.style.Pack(text_align="center", padding=5))
                    ],
                    style=toga.style.Pack(direction="column", padding=20)
                )
                self.main_window.content = error_box
            
            self.main_window.show()
            logger.info("Main window displayed")
            
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            # Create a minimal window as last resort
            try:
                self.main_window = toga.MainWindow(title="AirClick - Error")
                error_label = toga.Label("Failed to initialize AirClick", style=toga.style.Pack(padding=20))
                self.main_window.content = error_label
                self.main_window.show()
            except Exception as final_e:
                logger.error(f"Complete failure to create window: {final_e}")


def main():
    return AirClick()
