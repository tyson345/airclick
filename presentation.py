import cv2
import mediapipe as mp
import pyautogui
import time

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)
last_action_time = 0
cooldown = 1.0  # seconds between gestures

def count_fingers(lmList):
    fingers = []
    tips = [8, 12, 16, 20]  # Index, middle, ring, pinky

    # Thumb
    if lmList[4].x < lmList[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for tip in tips:
        if lmList[tip].y < lmList[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        lmList = hand.landmark
        mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

        fingers = count_fingers(lmList)
        total = sum(fingers)
        current_time = time.time()

        if current_time - last_action_time > cooldown:
            if total == 5:
                pyautogui.press('f5')
                cv2.putText(img, "Start Presentation", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                last_action_time = current_time

            elif total == 0:
                pyautogui.press('esc')
                cv2.putText(img, "Exit Presentation", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                last_action_time = current_time

            elif fingers == [0, 1, 0, 0, 0]:  # Index only
                pyautogui.press('right')
                cv2.putText(img, "Next Slide", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                last_action_time = current_time

            elif fingers == [0, 1, 1, 0, 0]:  # Index + Middle
                pyautogui.press('left')
                cv2.putText(img, "Previous Slide", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                last_action_time = current_time

    else:
        cv2.putText(img, "No Hand Detected", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

    cv2.imshow("Presentation Mode", img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
        break

cap.release()
cv2.destroyAllWindows()
