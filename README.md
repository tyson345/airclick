# Gesture Control Hub

A comprehensive gesture control application that allows you to control your computer using hand gestures through your webcam.

## Features

- **Regular Mode**: Standard mouse control with cursor movement, clicks, and scrolling
- **Movie Mode**: Optimized for media playback and streaming
- **Game Mode**: Enhanced precision for gaming applications
- **Presentation Mode**: Perfect for presentations and public speaking
- **Camera Mode**: Take photos and record videos using hand gestures
- **Game Mode**: Enhanced precision for gaming applications (includes Dino Fist Game)
- **AI Server Management**: Start/stop Python WebSocket server for advanced gesture detection

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application (choose one method):

   **Option A - Using startup script (recommended):**
   ```bash
   python start.py
   ```

   **Option B - Direct Flask app:**
   ```bash
   python app.py
   ```

3. Open your web browser and navigate to `http://localhost:5000`

## Usage

### Regular Mode
- **4 fingers up**: Move cursor
- **Index finger only**: Left click
- **Middle finger only**: Right click
- **Thumb only**: Scroll up
- **Index finger only (different gesture)**: Scroll down
- **Fist (all fingers down)**: Take screenshot

### Camera Mode
- **2 fingers**: Take a photo
- **3 fingers**: Start recording video
- **1 finger**: Stop recording video
- **Press 'q'**: Quit camera mode

### Game Mode
- **Enhanced Precision**: Optimized for gaming applications
- **Dino Fist Game**: Make a FIST to jump over obstacles using AI-powered hand detection
- **Python WebSocket Server**: Advanced MediaPipe-based gesture recognition
- **Real-time Processing**: Low latency gesture detection



### Other Modes
Each mode has its own optimized gesture controls for specific use cases.

## Controls

- Click on any mode button to activate that mode
- Click the "Close Mode" button to stop the current mode
- The status indicator shows which mode is currently active

## Requirements

- Python 3.7+
- Webcam
- Windows/Linux/macOS

## Dependencies

- Flask: Web framework
- OpenCV: Computer vision
- MediaPipe: Hand tracking
- PyAutoGUI: Mouse/keyboard control
- NumPy: Numerical computing
- WebSockets: Real-time communication for AI server

## Troubleshooting

1. **Camera not working**: Make sure your webcam is connected and not being used by another application
2. **Gestures not detected**: Ensure good lighting and keep your hand clearly visible to the camera
3. **Performance issues**: Close other applications that might be using the camera

## License

© 2025 Sourabh | All rights reserved 