import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)
mp_draw = mp.solutions.drawing_utils

# Video capture
cap = cv2.VideoCapture(0)
last_action_time = 0
cooldown = 2  # 2 seconds cooldown

def count_fingers(hand_landmarks):
    finger_tips = [8, 12, 16, 20]  # index, middle, ring, pinky
    finger_pips = [6, 10, 14, 18]  # corresponding PIP joints
    finger_names = ['index', 'middle', 'ring', 'pinky']
    finger_states = {name: False for name in finger_names}
    
    # Calculate hand orientation (left or right)
    wrist = hand_landmarks.landmark[0]
    pinky_mcp = hand_landmarks.landmark[17]
    is_right_hand = wrist.x < pinky_mcp.x
    
    # Thumb detection (different logic for left/right hands)
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    if (is_right_hand and thumb_tip.x > thumb_ip.x + 0.05) or (not is_right_hand and thumb_tip.x < thumb_ip.x - 0.05):
        thumb_extended = True
    else:
        thumb_extended = False
    
    # Finger detection (compare y coordinates)
    extended_fingers = []
    for tip, pip, name in zip(finger_tips, finger_pips, finger_names):
        tip_y = hand_landmarks.landmark[tip].y
        pip_y = hand_landmarks.landmark[pip].y
        
        # Finger is extended if tip is above PIP joint (with threshold)
        if tip_y < pip_y - 0.05:  # Added threshold to prevent false positives
            finger_states[name] = True
            extended_fingers.append(name)
    
    # Count only the clearly extended fingers
    count = sum(finger_states.values())
    
    # Debug information
    debug_text = f"Extended: {', '.join(extended_fingers) if extended_fingers else 'None'}"
    
    return count, finger_states, debug_text

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            fingers, finger_states, debug_text = count_fingers(handLms)
            
            # Display debug information
            cv2.putText(img, f"Count: {fingers}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(img, debug_text, (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            now = time.time()
            if now - last_action_time > cooldown:
                if fingers == 1 and finger_states['index'] and not any([finger_states['middle'], finger_states['ring'], finger_states['pinky']]):
                    pyautogui.press('k')  # Play/Pause
                    print("ACTION: Play/Pause")
                    last_action_time = now
                elif fingers == 2 and finger_states['index'] and finger_states['middle'] and not any([finger_states['ring'], finger_states['pinky']]):
                    pyautogui.press('l')  # Fast forward
                    print("ACTION: Forward")
                    last_action_time = now
                elif fingers == 3 and finger_states['index'] and finger_states['middle'] and finger_states['ring'] and not finger_states['pinky']:
                    pyautogui.press('j')  # Rewind
                    print("ACTION: Rewind")
                    last_action_time = now
                elif fingers == 4:
                    pyautogui.press('f')  # Fullscreen
                    print("ACTION: Fullscreen")
                    last_action_time = now

    cv2.imshow("YouTube Controller", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()