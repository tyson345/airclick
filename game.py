import pygame
import random
import cv2
import mediapipe as mp
import time

# ========== Gesture Setup ==========
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
jump_gesture_cooldown = 0
jump_delay = 1.0

# ========== Game Setup ==========
pygame.init()
WIDTH, HEIGHT = 800, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Jump with Gesture")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (200,0,0)
GREEN = (0,200,0)

# Dino
dino = pygame.Rect(100, 300, 50, 50)
gravity = 0.6
velocity = 0
jumping = False

# Cactus
cactus = pygame.Rect(WIDTH, 310, 20, 40)
cactus_speed = 6

# Score
score = 0
game_over = False

# Gesture detection
def is_jump_gesture(landmarks):
    if not landmarks:
        return False
    fingers = []
    tips = [8, 12, 16, 20]
    fingers.append(1 if landmarks[4].x < landmarks[3].x else 0)  # Thumb
    for tip in tips:
        fingers.append(1 if landmarks[tip].y < landmarks[tip - 2].y else 0)
    return sum(fingers) == 5  # Full hand open

# ========== Game Loop ==========
running = True
while running:
    win.fill(WHITE)

    # Check gesture input
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    now = time.time()

    if results.multi_hand_landmarks:
        lmList = results.multi_hand_landmarks[0].landmark
        if is_jump_gesture(lmList) and not jumping and now - jump_gesture_cooldown > jump_delay:
            velocity = -12
            jumping = True
            jump_gesture_cooldown = now

    # Dino jump physics
    velocity += gravity
    dino.y += velocity
    if dino.y >= 300:
        dino.y = 300
        velocity = 0
        jumping = False

    # Move cactus
    cactus.x -= cactus_speed
    if cactus.x < -20:
        cactus.x = WIDTH + random.randint(0, 200)
        score += 1

    # Collision detection
    if dino.colliderect(cactus):
        game_over = True

    # Draw
    pygame.draw.rect(win, GREEN, dino)
    pygame.draw.rect(win, RED, cactus)
    score_text = font.render(f"Score: {score}", True, BLACK)
    win.blit(score_text, (10, 10))

    if game_over:
        over_text = font.render("Game Over! Press R to Restart", True, RED)
        win.blit(over_text, (WIDTH//2 - 180, HEIGHT//2))
        pygame.display.update()
        key = None
        while key != pygame.K_r:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    key = pygame.K_r
                elif event.type == pygame.KEYDOWN:
                    key = event.key
        # Reset
        dino.y = 300
        cactus.x = WIDTH
        velocity = 0
        jumping = False
        score = 0
        game_over = False

    pygame.display.update()
    clock.tick(60)

    # Exit key
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

cap.release()
pygame.quit()
cv2.destroyAllWindows()