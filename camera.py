import cv2
import mediapipe as mp
import time
from collections import deque

class CameraGestureControl:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.recording = False
        self.video_writer = None
        self.finger_history = deque(maxlen=5)
        self.last_action_time = 0
        self.action_delay = 1  # seconds between actions
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def count_fingers(self, landmarks):
        """Count extended fingers using MediaPipe landmarks"""
        tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        thumb_tip = 4
        fingers = 0
        
        # Check thumb (different logic)
        if landmarks[thumb_tip].x < landmarks[thumb_tip - 1].x:
            fingers += 1
        
        # Check other fingers
        for tip in tips:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers += 1
                
        return fingers
    
    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        
        finger_count = 0
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks for visualization
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Count fingers
                finger_count = self.count_fingers(hand_landmarks.landmark)
                self.finger_history.append(finger_count)
                
                # Get most stable count from history
                if len(self.finger_history) == self.finger_history.maxlen:
                    finger_count = max(set(self.finger_history), 
                                      key=list(self.finger_history).count)
        
        # Display finger count
        cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Process actions
        current_time = time.time()
        
        # Photo capture (2 fingers)
        if finger_count == 2 and (current_time - self.last_action_time > self.action_delay):
            filename = f"photo_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Photo captured: {filename}")
            self.last_action_time = current_time
            cv2.putText(frame, "PHOTO TAKEN!", (50, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Start recording (3 fingers)
        if finger_count == 3 and not self.recording and (current_time - self.last_action_time > self.action_delay):
            self.recording = True
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            filename = f"video_{time.strftime('%Y%m%d_%H%M%S')}.avi"
            self.video_writer = cv2.VideoWriter(
                filename, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
            print(f"Started recording: {filename}")
            cv2.putText(frame, "RECORDING STARTED", (50, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.last_action_time = current_time
        
        # Stop recording (1 finger)
        if finger_count == 1 and self.recording:
            self.recording = False
            self.video_writer.release()
            print("Recording stopped")
            cv2.putText(frame, "RECORDING STOPPED", (50, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.last_action_time = current_time
        
        # Record frame if recording
        if self.recording:
            self.video_writer.write(frame)
            cv2.circle(frame, (frame.shape[1] - 30, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "RECORDING...", (frame.shape[1] - 150, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame
    
    def run(self):
        print("Camera Gesture Control started:")
        print("- Show 2 fingers: Take photo")
        print("- Show 3 fingers: Start recording")
        print("- Show 1 finger: Stop recording")
        print("- Press 'q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            frame = self.process_frame(frame)
            cv2.imshow('Camera Gesture Control (Press Q to quit)', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Stop recording if quitting while recording
                if self.recording:
                    self.recording = False
                    self.video_writer.release()
                    print("Recording stopped on exit")
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    control = CameraGestureControl()
    control.run()
