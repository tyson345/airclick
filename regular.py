import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Screen size
screen_w, screen_h = pyautogui.size()

# Webcam settings
cam_w, cam_h = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, cam_w)
cap.set(4, cam_h)

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Previous location for smooth movement
prev_x, prev_y = 0, 0
smoothening = 7  # Higher = smoother & slower

# Cooldowns
click_delay = 1  # in seconds
last_left_click = 0
last_right_click = 0
last_scroll = 0
last_screenshot = 0
screenshot_delay = 1  # seconds

def fingers_up(lmList):
    tips = [8, 12, 16, 20]
    fingers = []
    for i, tip in enumerate(tips):
        if lmList[tip].y < lmList[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Mirror image
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            lmList = hand.landmark

            mp_draw.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)

            # Get index finger coordinates
            x1 = int(lmList[8].x * cam_w)
            y1 = int(lmList[8].y * cam_h)

            # Convert to screen coordinates
            screen_x = np.interp(x1, (100, cam_w - 100), (0, screen_w))
            screen_y = np.interp(y1, (100, cam_h - 100), (0, screen_h))

            # Smooth movement
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # Get finger status
            fingers = fingers_up(lmList)

            # Perform actions
            current_time = time.time()

            if fingers == [1, 1, 1, 1]:
                cv2.putText(img, "Move Cursor", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            elif fingers[0] == 1 and fingers[1] == 0 and (current_time - last_left_click > click_delay):
                pyautogui.click()
                last_left_click = current_time
                cv2.putText(img, "Left Click", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

            elif fingers[0] == 0 and fingers[1] == 1 and (current_time - last_right_click > click_delay):
                pyautogui.rightClick()
                last_right_click = current_time
                cv2.putText(img, "Right Click", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

            elif fingers == [1, 0, 0, 0] and (current_time - last_scroll > 0.3):
                pyautogui.scroll(40)
                last_scroll = current_time
                cv2.putText(img, "Scroll Up", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

            elif fingers == [0, 1, 0, 0] and (current_time - last_scroll > 0.3):
                pyautogui.scroll(-40)
                last_scroll = current_time
                cv2.putText(img, "Scroll Down", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

            # Screenshot when all fingers are down (fist)
            elif fingers == [0, 0, 0, 0] and (current_time - last_screenshot > screenshot_delay):
                screenshot = pyautogui.screenshot()
                filename = f"screenshot_{int(time.time())}.png"
                screenshot.save(filename)
                last_screenshot = current_time
                cv2.putText(img, "Screenshot Taken", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,128,255), 2)

    else:
        cv2.putText(img, "No Hand Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 0, 200), 2)

    # Display the output
    cv2.imshow("Virtual Mouse", img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
