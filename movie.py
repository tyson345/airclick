import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
last_action_time = 0

def count_fingers(hand_landmarks):
    tips = [8, 12, 16]  # index, middle, ring
    count = 0
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    return count

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
            fingers = count_fingers(handLms)

            now = time.time()
            if now - last_action_time > 1.5:
                if fingers == 1:
                    pyautogui.press('k')  # Play/Pause
                    last_action_time = now
                elif fingers == 2:
                    pyautogui.press('l')  # Fast forward
                    last_action_time = now
                elif fingers == 3:
                    pyautogui.press('j')  # Rewind
                    last_action_time = now

    cv2.imshow("YouTube Controller", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
