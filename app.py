from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import signal
import threading
import time

app = Flask(__name__)
processes = {}
current_mode = None
websocket_server_process = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dino-game')
def dino_game():
    return send_from_directory('.', 'dino-game.html')

@app.route('/dino-gesture')
def dino_gesture():
    return send_from_directory('.', 'dino_gesture.html')


@app.route('/start-websocket-server', methods=['POST'])
def start_websocket_server():
    global websocket_server_process
    try:
        if websocket_server_process is None or websocket_server_process.poll() is not None:
            websocket_server_process = subprocess.Popen(["python", "hand_detection_server.py"])
            time.sleep(2)  # Give server time to start
            return jsonify({
                "message": "WebSocket server started successfully",
                "status": "success"
            })
        else:
            return jsonify({
                "message": "WebSocket server is already running",
                "status": "info"
            })
    except Exception as e:
        return jsonify({
            "message": f"Error starting WebSocket server: {str(e)}",
            "status": "error"
        })

@app.route('/stop-websocket-server', methods=['POST'])
def stop_websocket_server():
    global websocket_server_process
    try:
        if websocket_server_process and websocket_server_process.poll() is None:
            websocket_server_process.terminate()
            websocket_server_process.wait(timeout=5)
            websocket_server_process = None
            return jsonify({
                "message": "WebSocket server stopped successfully",
                "status": "success"
            })
        else:
            return jsonify({
                "message": "No WebSocket server running",
                "status": "info"
            })
    except Exception as e:
        return jsonify({
            "message": f"Error stopping WebSocket server: {str(e)}",
            "status": "error"
        })

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

@app.route('/close', methods=['POST'])
def close_mode():
    global current_mode
    data = request.get_json()
    mode = data.get('mode')

    proc = processes.get(mode)
    if proc and proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=5)  # Wait up to 5 seconds for graceful termination
        except subprocess.TimeoutExpired:
            proc.kill()  # Force kill if it doesn't terminate gracefully
        
        processes.pop(mode, None)
        current_mode = None
        return jsonify({
            "message": f"{mode.capitalize()} Mode Closed Successfully", 
            "active": None,
            "status": "success"
        })
    else:
        return jsonify({
            "message": f"No active {mode} process to close", 
            "active": current_mode,
            "status": "info"
        })

@app.route('/status', methods=['GET'])
def get_status():
    global current_mode
    # Check if current process is still running
    if current_mode and current_mode in processes:
        proc = processes[current_mode]
        if proc.poll() is not None:  # Process has terminated
            processes.pop(current_mode, None)
            current_mode = None
    
    return jsonify({"active": current_mode})

def stop_all_processes():
    global current_mode
    for mode, proc in list(processes.items()):
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    processes.clear()
    current_mode = None

@app.route('/shutdown', methods=['POST'])
def shutdown():
    stop_all_processes()
    # Also stop WebSocket server
    global websocket_server_process
    if websocket_server_process and websocket_server_process.poll() is None:
        websocket_server_process.terminate()
    return jsonify({"message": "All processes stopped", "status": "success"})

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        stop_all_processes()
        # Stop WebSocket server on exit
        if websocket_server_process and websocket_server_process.poll() is None:
            websocket_server_process.terminate()