import cv2
import mediapipe as mp
import numpy as np
import asyncio
import websockets
import json
import base64
import time

class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,  # Increased from 0.5 for better accuracy
            min_tracking_confidence=0.5,   # Increased from 0.4 for better tracking
            model_complexity=1             # Increased from 0 for better accuracy
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.consecutive_fist_frames = 0
        self.required_fist_frames = 3      # Increased from 1 for more stable detection
        self.consecutive_no_fist_frames = 0
        self.required_no_fist_frames = 2   # Prevent false positives

    def detect_fist(self, landmarks):
        if not landmarks:
            return False
        
        # More precise finger detection with better thresholds
        # Index finger (8) should be below middle joint (6)
        index_folded = landmarks[8].y > landmarks[6].y + 0.02
        
        # Middle finger (12) should be below middle joint (10)
        middle_folded = landmarks[12].y > landmarks[10].y + 0.02
        
        # Ring finger (16) should be below middle joint (14)
        ring_folded = landmarks[16].y > landmarks[14].y + 0.02
        
        # Pinky finger (20) should be below middle joint (18)
        pinky_folded = landmarks[20].y > landmarks[18].y + 0.02
        
        # Thumb should be close to index finger base (thumb tip 4 near index base 5)
        thumb_distance = np.sqrt(
            (landmarks[4].x - landmarks[5].x)**2 + 
            (landmarks[4].y - landmarks[5].y)**2
        )
        thumb_folded = thumb_distance < 0.15
        
        # Additional check: all fingertips should be below their respective middle joints
        fingertips_below = (
            landmarks[8].y > landmarks[5].y and  # Index tip below base
            landmarks[12].y > landmarks[9].y and  # Middle tip below base
            landmarks[16].y > landmarks[13].y and # Ring tip below base
            landmarks[20].y > landmarks[17].y     # Pinky tip below base
        )
        
        # All conditions must be met for a proper fist
        all_folded = (index_folded and middle_folded and ring_folded and 
                     pinky_folded and thumb_folded and fingertips_below)
        
        return all_folded

    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (160, 120))
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        detection_result = {
            'hand_detected': False,
            'fist_detected': False,
            'landmarks': [],
            'confidence': 0.0,
            'debug_info': 'No hand detected'
        }
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            is_fist = self.detect_fist(landmarks)
            
            # Improved stability logic
            if is_fist:
                self.consecutive_fist_frames += 1
                self.consecutive_no_fist_frames = 0
            else:
                self.consecutive_no_fist_frames += 1
                # Only reset fist frames if we've seen no fist for required frames
                if self.consecutive_no_fist_frames >= self.required_no_fist_frames:
                    self.consecutive_fist_frames = 0
            
            # More stable detection: require consecutive frames for both detection and release
            stable_fist = self.consecutive_fist_frames >= self.required_fist_frames
            
            detection_result['hand_detected'] = True
            detection_result['fist_detected'] = stable_fist
            detection_result['landmarks'] = [
                {'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in landmarks
            ]
            # Higher confidence for stable detection
            detection_result['confidence'] = 0.95 if stable_fist else 0.6
            detection_result['consecutive_frames'] = self.consecutive_fist_frames
            detection_result['no_fist_frames'] = self.consecutive_no_fist_frames
            detection_result['debug_info'] = f'Hand detected - Fist: {is_fist}, Stable: {stable_fist}'
        else:
            detection_result['debug_info'] = 'No hand landmarks found'
            
        return detection_result, small_frame

class WebSocketServer:
    def __init__(self):
        self.detector = HandGestureDetector()
        self.clients = set()

    async def register_client(self, websocket):
        self.clients.add(websocket)
        print(f"✅ Client connected. Total clients: {len(self.clients)}")

    async def unregister_client(self, websocket):
        self.clients.discard(websocket)
        print(f"❌ Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_detection(self, detection_result):
        if self.clients:
            message = json.dumps({
                'type': 'gesture_detection',
                'data': detection_result
            })
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
                except Exception as e:
                    print(f"Error sending to client: {e}")
                    disconnected.add(client)
            for client in disconnected:
                self.clients.discard(client)

    async def handle_client(self, websocket):
        await self.register_client(websocket)
        frame_count = 0
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data['type'] == 'video_frame':
                        frame_count += 1
                        image_data = base64.b64decode(data['frame'].split(',')[1])
                        nparr = np.frombuffer(image_data, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if frame is not None:
                            detection_result, _ = self.detector.process_frame(frame)
                            await self.broadcast_detection(detection_result)
                            
                            # Debug output every 30 frames (about once per second)
                            if frame_count % 30 == 0:
                                print(f"📊 Frame {frame_count}: {detection_result['debug_info']}")
                        else:
                            print("❌ Failed to decode video frame")
                    elif data['type'] == 'update_settings':
                        if 'stability_frames' in data:
                            self.detector.required_fist_frames = data['stability_frames']
                            print(f"✅ Updated stability frames to: {data['stability_frames']}")
                    elif data['type'] == 'test_message':
                        print(f"🧪 Test message received: {data.get('message', 'No message')}")
                        # Send back a test response
                        await websocket.send(json.dumps({
                            'type': 'test_response',
                            'message': 'Server is working correctly!',
                            'timestamp': time.time()
                        }))
                except json.JSONDecodeError:
                    print("❌ Invalid JSON received from client")
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Client connection closed")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            await self.unregister_client(websocket)

def main():
    print("🚀 Starting Hand Gesture Detection Server...")
    print("📡 Server will run on ws://localhost:8765")
    print("📦 Make sure to install required packages:")
    print("   pip install opencv-python mediapipe websockets numpy")
    print()
    server = WebSocketServer()
    async def start_server():
        print("✅ Server started! Open the HTML file in your browser.")
        print("✊ Make a FIST to control the dino!")
        print("🔄 Waiting for connections...")
        print()
        async with websockets.serve(server.handle_client, "localhost", 8765):
            await asyncio.Future()
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()