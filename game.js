let dino = { y: 300, vy: 0, gravity: 1.5, jumping: false };
let canvas = document.getElementById('gameCanvas');
let ctx = canvas.getContext('2d');
let gestureStatus = document.getElementById('gestureStatus');

function startGame() {
  gestureStatus.innerText = 'Gesture: Waiting...';
  setupCameraAndGesture();
  requestAnimationFrame(update);
}

function jump() {
  if (!dino.jumping) {
    dino.vy = -20;
    dino.jumping = true;
  }
}

function update() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // gravity
  dino.y += dino.vy;
  dino.vy += dino.gravity;

  if (dino.y >= 300) {
    dino.y = 300;
    dino.vy = 0;
    dino.jumping = false;
  }

  ctx.fillStyle = 'brown';
  ctx.fillRect(100, dino.y, 50, 50);

  requestAnimationFrame(update);
}

function setupCameraAndGesture() {
  const video = document.getElementById('video');
  const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 0,
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.7
  });

  hands.onResults((results) => {
    if (results.multiHandLandmarks.length > 0) {
      gestureStatus.innerText = 'Gesture: Hand Detected';
      const landmarks = results.multiHandLandmarks[0];

      // basic fist check
      const isFist = landmarks[8].y > landmarks[6].y && landmarks[12].y > landmarks[10].y;
      if (isFist) {
        jump();
        gestureStatus.innerText = 'Gesture: FIST (Jump)';
      }
    } else {
      gestureStatus.innerText = 'Gesture: NONE';
    }
  });

  const camera = new Camera(video, {
    onFrame: async () => {
      await hands.send({ image: video });
    },
    width: 640,
    height: 480
  });

  camera.start();
}
