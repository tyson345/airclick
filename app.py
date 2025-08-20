from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import signal
import threading
import time
import webbrowser
import pyautogui
from datetime import datetime
import tempfile
from voice import VoiceAssistant
import sys

app = Flask(__name__)
processes = {}
current_mode = None
websocket_server_process = None

def signal_handler(sig, frame):
    # Cleanup code here (release camera, etc.)
    print("Received termination signal, cleaning up...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dino-game')
def dino_game():
    return send_from_directory('.', 'dino-game.html')

@app.route('/dino-gesture')
def dino_gesture():
    return send_from_directory('.', 'dino_gesture.html')

@app.route('/test')
def test():
    return "<h1>Flask Server is Working!</h1><p>If you see this, the server is running correctly.</p>"

@app.route('/process-voice-command', methods=['POST'])
def process_voice_command():
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
        # Create a temporary voice assistant to process the command
        assistant = VoiceAssistant()
        
        response = ""
        
        # Weather
        if "weather" in command:
            response = assistant.get_weather()
        
        # News
        elif "full news" in command:
            response = assistant.get_news(full=True)
        elif "news" in command or "update" in command:
            response = assistant.get_news(full=False)
        
        # Timer
        elif "set timer" in command:
            try:
                seconds = int(''.join([c for c in command if c.isdigit()]))
                if seconds > 0:
                    response = assistant.set_timer(seconds)
                else:
                    response = "Please specify a valid number of seconds."
            except:
                response = "Please tell me the timer duration in seconds."
        
        # System info
        elif "system info" in command or "status" in command:
            response = assistant.get_system_info()
        
        # Search
        elif command.startswith("search"):
            query = command.replace("search", "").strip()
            response = assistant.search_google(query) if query else "What should I search for?"
        
        # Websites
        elif "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            response = "Opening YouTube"
        elif "open google" in command:
            webbrowser.open("https://www.google.com")
            response = "Opening Google"
        elif "open gmail" in command:
            webbrowser.open("https://mail.google.com")
            response = "Opening Gmail"
        elif "open whatsapp" in command:
            webbrowser.open("https://web.whatsapp.com")
            response = "Opening WhatsApp Web"
        elif "open instagram" in command:
            webbrowser.open("https://www.instagram.com")
            response = "Opening Instagram"
        elif "open facebook" in command:
            webbrowser.open("https://www.facebook.com")
            response = "Opening Facebook"
        elif "open twitter" in command:
            webbrowser.open("https://twitter.com")
            response = "Opening Twitter"
        elif "open linkedin" in command:
            webbrowser.open("https://www.linkedin.com")
            response = "Opening LinkedIn"
        
        # Local apps
        elif "open notepad" in command:
            response = assistant.open_app("notepad.exe")
        elif "open calculator" in command:
            response = assistant.open_app("calc.exe")
        elif "open paint" in command:
            response = assistant.open_app("mspaint.exe")
        
        # Name
        elif "your name" in command:
            response = "I am AirClick Voice Assistant, your AI-powered companion"
        
        else:
            response = "I don't understand that command yet. Try asking about weather, news, opening websites, or setting timers."
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save-note', methods=['POST'])
def save_note():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"success": False, "error": "No text provided"})
        
        # Create notes folder if it doesn't exist
        notes_folder = "saved_notes"
        if not os.path.exists(notes_folder):
            os.makedirs(notes_folder)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"note_{timestamp}.txt"
        filepath = os.path.join(notes_folder, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Note: {text}\n")
        
        # Open in notepad (Windows) or default text editor
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['notepad.exe', filepath])
            else:  # Linux/Mac
                subprocess.Popen(['gedit', filepath])  # or 'nano', 'vim'
        except:
            pass  # If can't open editor, just save the file
        
        return jsonify({"success": True, "filename": filename})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/send-to-social', methods=['POST'])
def send_to_social():
    try:
        data = request.get_json()
        text = data.get('text', '')
        platform = data.get('platform', '')
        
        if not text or not platform:
            return jsonify({"success": False, "error": "Missing text or platform"})
        
        # Open the appropriate social media platform
        if platform == 'whatsapp':
            webbrowser.open("https://web.whatsapp.com")
            time.sleep(3)  # Wait for page to load
            pyautogui.typewrite(text)
            message = "Message typed in WhatsApp. Select a contact and press Enter to send."
            
        elif platform == 'twitter':
            webbrowser.open("https://twitter.com/compose/tweet")
            time.sleep(3)
            pyautogui.typewrite(text)
            message = "Message typed in Twitter. Click Tweet to send."
            
        elif platform == 'facebook':
            webbrowser.open("https://www.facebook.com")
            time.sleep(3)
            pyautogui.typewrite(text)
            message = "Message typed in Facebook. Click in the post box first if needed."
            
        elif platform == 'instagram':
            webbrowser.open("https://www.instagram.com")
            message = f"Instagram opened. Your message: {text}"
            
        elif platform == 'linkedin':
            webbrowser.open("https://www.linkedin.com")
            time.sleep(3)
            pyautogui.typewrite(text)
            message = "Message typed in LinkedIn. Click in the post area first if needed."
            
        else:
            return jsonify({"success": False, "error": "Unsupported platform"})
        
        return jsonify({"success": True, "message": message})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/run', methods=['POST'])
def run_mode():
    global current_mode
    data = request.get_json()
    mode = data.get('mode')

    # Stop any existing process
    stop_all_processes()

    try:
        if mode == 'regular':
            proc = subprocess.Popen(["python", "regular.py"])
        elif mode == 'movie':
            proc = subprocess.Popen(["python", "movie.py"])
        elif mode == 'game':
            proc = subprocess.Popen(["python", "game.py"])
        elif mode == 'presentation':
            proc = subprocess.Popen(["python", "presentation.py"])
        elif mode == 'camera':
            proc = subprocess.Popen(["python", "camera.py"])
        elif mode == 'websocket':
            proc = subprocess.Popen(["python", "hand_detection_server.py"])
        else:
            return jsonify({"message": "Invalid mode", "active": None, "status": "error"})

        processes[mode] = proc
        current_mode = mode
        return jsonify({
            "message": f"{mode.capitalize()} Mode Activated Successfully", 
            "active": mode,
            "status": "success"
        })
        
    except FileNotFoundError:
        return jsonify({
            "message": f"Error: {mode}.py not found", 
            "active": None,
            "status": "error"
        })
    except Exception as e:
        return jsonify({
            "message": f"Error starting {mode} mode: {str(e)}", 
            "active": None,
            "status": "error"
        })

@app.route('/stop_mode', methods=['POST'])
def stop_mode():
    global current_mode
    data = request.get_json()
    mode = data.get('mode')
    
    try:
        if mode and mode in processes:
            proc = processes[mode]
            if proc and proc.poll() is None:
                try:
                    # For camera mode, ensure proper cleanup
                    if mode == 'camera':
                        proc.terminate()
                        proc.wait(timeout=5)  # Give more time for camera cleanup
                    else:
                        proc.terminate()
                        proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                
                del processes[mode]
                if current_mode == mode:
                    current_mode = None
                
                return jsonify({
                    "success": True,
                    "message": f"{mode.capitalize()} Mode Stopped Successfully",
                    "active": None,
                    "status": "success"
                })
        
        # If no specific mode or mode not found, stop all
        stop_all_processes()
        return jsonify({
            "success": True,
            "message": "All modes stopped",
            "active": None, 
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": f"Error stopping {mode} mode: {str(e)}",
            "active": current_mode,
            "status": "error"
        })

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "active": current_mode,
        "running_processes": list(processes.keys())
    })

def stop_all_processes():
    global current_mode
    
    # Stop other processes
    for mode, proc in list(processes.items()):
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    processes.clear()
    current_mode = None

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        stop_all_processes()
from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import signal
import threading
import time
import webbrowser
import pyautogui
from datetime import datetime
import tempfile
from voice import VoiceAssistant

app = Flask(__name__)
processes = {}
current_mode = None
websocket_server_process = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dino-game')
def dino_game():
    return send_from_directory('.', 'dino-game.html')

@app.route('/dino-gesture')
def dino_gesture():
    return send_from_directory('.', 'dino_gesture.html')

@app.route('/test')
def test():
    return "<h1>Flask Server is Working!</h1><p>If you see this, the server is running correctly.</p>"

@app.route('/process-voice-command', methods=['POST'])
def process_voice_command():
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
        # Create a temporary voice assistant to process the command
        assistant = VoiceAssistant()
        
        response = ""
        
        # Weather
        if "weather" in command:
            response = assistant.get_weather()
        
        # News
        elif "full news" in command:
            response = assistant.get_news(full=True)
        elif "news" in command or "update" in command:
            response = assistant.get_news(full=False)
        
        # Timer
        elif "set timer" in command:
            try:
                seconds = int(''.join([c for c in command if c.isdigit()]))
                if seconds > 0:
                    response = assistant.set_timer(seconds)
                else:
                    response = "Please specify a valid number of seconds."
            except:
                response = "Please tell me the timer duration in seconds."
        
        # System info
        elif "system info" in command or "status" in command:
            response = assistant.get_system_info()
        
        # Search
        elif command.startswith("search"):
            query = command.replace("search", "").strip()
            response = assistant.search_google(query) if query else "What should I search for?"
        
        # Websites
        elif "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            response = "Opening YouTube"
        elif "open google" in command:
            webbrowser.open("https://www.google.com")
            response = "Opening Google"
        elif "open gmail" in command:
            webbrowser.open("https://mail.google.com")
            response = "Opening Gmail"
        elif "open whatsapp" in command:
            webbrowser.open("https://web.whatsapp.com")
            response = "Opening WhatsApp Web"
        elif "open instagram" in command:
            webbrowser.open("https://www.instagram.com")
            response = "Opening Instagram"
        elif "open facebook" in command:
            webbrowser.open("https://www.facebook.com")
            response = "Opening Facebook"
        elif "open twitter" in command:
            webbrowser.open("https://twitter.com")
            response = "Opening Twitter"
        elif "open linkedin" in command:
            webbrowser.open("https://www.linkedin.com")
            response = "Opening LinkedIn"
        
        # Local apps
        elif "open notepad" in command:
            response = assistant.open_app("notepad.exe")
        elif "open calculator" in command:
            response = assistant.open_app("calc.exe")
        elif "open paint" in command:
            response = assistant.open_app("mspaint.exe")
        
        # Name
        elif "your name" in command:
            response = "I am AirClick Voice Assistant, your AI-powered companion"
        
        else:
            response = "I don't understand that command yet. Try asking about weather, news, opening websites, or setting timers."
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save-note', methods=['POST'])
def save_note():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"success": False, "error": "No text provided"})
        
        # Create notes folder if it doesn't exist
        notes_folder = "saved_notes"
        if not os.path.exists(notes_folder):
            os.makedirs(notes_folder)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"note_{timestamp}.txt"
        filepath = os.path.join(notes_folder, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Note: {text}\n")
        
        # Open in notepad (Windows) or default text editor
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['notepad.exe', filepath])
            else:  # Linux/Mac
                subprocess.Popen(['gedit', filepath])  # or 'nano', 'vim'
        except:
            pass  # If can't open editor, just save the file
        
        return jsonify({"success": True, "filename": filename})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/send-to-social', methods=['POST'])
def send_to_social():
    try:
        data = request.get_json()
        text = data.get('text', '')
        platform = data.get('platform', '')
        
        if not text or not platform:
            return jsonify({"success": False, "error": "Missing text or platform"})
        
        # Open the appropriate social media platform
        if platform == 'whatsapp':
            webbrowser.open("https://web.whatsapp.com")
            time.sleep(3)  # Wait for page to load
            pyautogui.typewrite(text)
            message = "Message typed in WhatsApp. Select a contact and press Enter to send."
            
        elif platform == 'twitter':
            webbrowser.open("https://twitter.com/compose/tweet")
            time.sleep(3)
            pyautogui.typewrite(text)
            message = "Message typed in Twitter. Click Tweet to send."
            
        elif platform == 'facebook':
            webbrowser.open("https://www.facebook.com")
            time.sleep(3)
            pyautogui.typewrite(text)
            message = "Message typed in Facebook. Click in the post box first if needed."
            
        elif platform == 'instagram':
            webbrowser.open("https://www.instagram.com")
            message = f"Instagram opened. Your message: {text}"
            
        elif platform == 'linkedin':
            webbrowser.open("https://www.linkedin.com")
            time.sleep(3)
            pyautogui.typewrite(text)
            message = "Message typed in LinkedIn. Click in the post area first if needed."
            
        else:
            return jsonify({"success": False, "error": "Unsupported platform"})
        
        return jsonify({"success": True, "message": message})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/run', methods=['POST'])
def run_mode():
    global current_mode
    data = request.get_json()
    mode = data.get('mode')

    # Stop any existing process
    stop_all_processes()

    try:
        if mode == 'regular':
            proc = subprocess.Popen(["python", "regular.py"])
        elif mode == 'movie':
            proc = subprocess.Popen(["python", "movie.py"])
        elif mode == 'game':
            proc = subprocess.Popen(["python", "game.py"])
        elif mode == 'presentation':
            proc = subprocess.Popen(["python", "presentation.py"])
        elif mode == 'camera':
            proc = subprocess.Popen(["python", "camera.py"])
        elif mode == 'websocket':
            proc = subprocess.Popen(["python", "hand_detection_server.py"])
        else:
            return jsonify({"message": "Invalid mode", "active": None, "status": "error"})

        processes[mode] = proc
        current_mode = mode
        return jsonify({
            "message": f"{mode.capitalize()} Mode Activated Successfully", 
            "active": mode,
            "status": "success"
        })
        
    except FileNotFoundError:
        return jsonify({
            "message": f"Error: {mode}.py not found", 
            "active": None,
            "status": "error"
        })
    except Exception as e:
        return jsonify({
            "message": f"Error starting {mode} mode: {str(e)}", 
            "active": None,
            "status": "error"
        })

@app.route('/stop_mode', methods=['POST'])
def stop_mode():
    global current_mode
    data = request.get_json()
    mode = data.get('mode')
    
    try:
        if mode and mode in processes:
            proc = processes[mode]
            if proc and proc.poll() is None:
                try:
                    # For camera mode, ensure proper cleanup
                    if mode == 'camera':
                        proc.terminate()
                        proc.wait(timeout=5)  # Give more time for camera cleanup
                    else:
                        proc.terminate()
                        proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                
                del processes[mode]
                if current_mode == mode:
                    current_mode = None
                
                return jsonify({
                    "success": True,
                    "message": f"{mode.capitalize()} Mode Stopped Successfully",
                    "active": None,
                    "status": "success"
                })
        
        # If no specific mode or mode not found, stop all
        stop_all_processes()
        return jsonify({
            "success": True,
            "message": "All modes stopped",
            "active": None, 
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": f"Error stopping {mode} mode: {str(e)}",
            "active": current_mode,
            "status": "error"
        })

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "active": current_mode,
        "running_processes": list(processes.keys())
    })

def stop_all_processes():
    global current_mode
    
    # Stop other processes
    for mode, proc in list(processes.items()):
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    processes.clear()
    current_mode = None

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        stop_all_processes()
