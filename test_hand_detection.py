#!/usr/bin/env python3
"""
Simple test script to verify hand detection is working
Run this to test if MediaPipe and hand detection are working properly
"""

import cv2
import mediapipe as mp
import numpy as np

def test_hand_detection():
    print("🧪 Testing Hand Detection System...")
    print("📦 Checking MediaPipe installation...")
    
    try:
        # Initialize MediaPipe Hands
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        print("✅ MediaPipe Hands initialized successfully")
        
        # Open camera
        print("📷 Opening camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Failed to open camera")
            return False
            
        print("✅ Camera opened successfully")
        print("👋 Show your hand to the camera")
        print("✊ Make a fist to test detection")
        print("Press 'q' to quit")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
                
            # Flip frame horizontally for selfie view
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            frame_count += 1
            
            # Draw hand landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Test fist detection
                    landmarks = hand_landmarks.landmark
                    
                    # Simple fist detection
                    index_folded = landmarks[8].y > landmarks[6].y + 0.02
                    middle_folded = landmarks[12].y > landmarks[10].y + 0.02
                    ring_folded = landmarks[16].y > landmarks[14].y + 0.02
                    pinky_folded = landmarks[20].y > landmarks[18].y + 0.02
                    
                    # Thumb distance check
                    thumb_distance = np.sqrt(
                        (landmarks[4].x - landmarks[5].x)**2 + 
                        (landmarks[4].y - landmarks[5].y)**2
                    )
                    thumb_folded = thumb_distance < 0.15
                    
                    # Fingertips below base check
                    fingertips_below = (
                        landmarks[8].y > landmarks[5].y and
                        landmarks[12].y > landmarks[9].y and
                        landmarks[16].y > landmarks[13].y and
                        landmarks[20].y > landmarks[17].y
                    )
                    
                    is_fist = (index_folded and middle_folded and ring_folded and 
                             pinky_folded and thumb_folded and fingertips_below)
                    
                    # Display status
                    if is_fist:
                        cv2.putText(frame, "FIST DETECTED!", (10, 50), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        print(f"✅ Frame {frame_count}: FIST DETECTED!")
                    else:
                        cv2.putText(frame, "Hand Detected (Not Fist)", (10, 50), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        if frame_count % 30 == 0:  # Print every 30 frames
                            print(f"📊 Frame {frame_count}: Hand detected but not a fist")
            else:
                cv2.putText(frame, "No Hand Detected", (10, 50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if frame_count % 30 == 0:  # Print every 30 frames
                    print(f"❌ Frame {frame_count}: No hand detected")
            
            # Display frame
            cv2.imshow('Hand Detection Test', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print("✅ Test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Hand Detection Test...")
    print("=" * 50)
    
    success = test_hand_detection()
    
    print("=" * 50)
    if success:
        print("🎉 Hand detection test completed successfully!")
        print("✅ Your system should work with the game")
    else:
        print("💥 Hand detection test failed!")
        print("❌ Please check your MediaPipe installation")
        print("💡 Try running: pip install mediapipe opencv-python") 