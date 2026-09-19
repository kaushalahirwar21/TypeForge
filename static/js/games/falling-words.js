/**
 * TypeRise Game 1: Falling Words
 * Words fall towards a danger zone. Type them before they hit the ground!
 */

class FallingWordsGame {
  constructor() {
    this.stage = document.getElementById('falling-words-stage');
    this.input = document.getElementById('falling-game-input');
    this.scoreDisplay = document.getElementById('falling-score');
    this.livesDisplay = document.getElementById('falling-lives');
    this.overlay = document.getElementById('falling-game-overlay');
    this.finalScoreDisplay = document.getElementById('falling-final-score');
    this.restartBtn = document.getElementById('falling-restart-btn');

    this.wordBank = [
      'quick', 'speed', 'touch', 'keyboard', 'focus', 'stream', 'flow',
      'spark', 'stride', 'swift', 'matrix', 'rhythm', 'cadence', 'laser',
      'motion', 'bright', 'action', 'charge', 'master', 'energy', 'zenith',
      'vector', 'hyper', 'pulse', 'glide', 'boost', 'turbo', 'agile'
    ];

    this.words = [];
    this.score = 0;
    this.lives = 3;
    this.speed = 1.0;
    this.isRunning = false;
    this.animationId = null;
    this.spawnTimer = null;

    this.init();
  }

  init() {
    if (!this.stage || !this.input) return;

    this.input.addEventListener('input', (e) => this.handleInput(e.target.value.trim().toLowerCase()));
    if (this.restartBtn) {
      this.restartBtn.addEventListener('click', () => this.start());
    }
  }

  start() {
    this.reset();
    this.isRunning = true;
    this.overlay.style.display = 'none';
    this.input.value = '';
    this.input.disabled = false;
    this.input.focus();

    this.loop();
    this.scheduleNextSpawn();
  }

  reset() {
    this.isRunning = false;
    cancelAnimationFrame(this.animationId);
    clearTimeout(this.spawnTimer);

    // Clear DOM words
    this.stage.querySelectorAll('.falling-word-bubble').forEach(el => el.remove());
    this.words = [];
    this.score = 0;
    this.lives = 3;
    this.speed = 1.0;

    this.updateHUD();
  }

  updateHUD() {
    if (this.scoreDisplay) this.scoreDisplay.textContent = this.score;
    if (this.livesDisplay) {
      this.livesDisplay.innerHTML = '❤️'.repeat(Math.max(0, this.lives)) + '🖤'.repeat(Math.max(0, 3 - this.lives));
    }
  }

  scheduleNextSpawn() {
    if (!this.isRunning) return;
    const interval = Math.max(900, 2400 - (this.score * 1.5));
    this.spawnTimer = setTimeout(() => {
      this.spawnWord();
      this.scheduleNextSpawn();
    }, interval);
  }

  spawnWord() {
    if (!this.isRunning) return;
    const randomWord = this.wordBank[Math.floor(Math.random() * this.wordBank.length)];

    const bubble = document.createElement('div');
    bubble.className = 'falling-word-bubble';
    bubble.textContent = randomWord;

    const stageWidth = this.stage.clientWidth - 120;
    const x = Math.max(10, Math.floor(Math.random() * stageWidth));
    const y = 0;

    bubble.style.left = `${x}px`;
    bubble.style.top = `${y}px`;
    this.stage.appendChild(bubble);

    this.words.push({
      text: randomWord,
      element: bubble,
      x: x,
      y: y,
    });
  }

  loop() {
    if (!this.isRunning) return;

    const stageHeight = this.stage.clientHeight - 40;

    for (let i = this.words.length - 1; i >= 0; i--) {
      const item = this.words[i];
      item.y += this.speed;
      item.element.style.top = `${item.y}px`;

      // Check if hit danger floor
      if (item.y >= stageHeight) {
        item.element.remove();
        this.words.splice(i, 1);
        this.lives--;
        this.updateHUD();

        if (window.typeforgeSound) window.typeforgeSound.playError();

        if (this.lives <= 0) {
          this.gameOver();
          return;
        }
      }
    }

    this.animationId = requestAnimationFrame(() => this.loop());
  }

  handleInput(val) {
    if (!this.isRunning || !val) return;

    // Check if typed value matches any falling word
    for (let i = 0; i < this.words.length; i++) {
      const item = this.words[i];

      if (item.text === val) {
        // Destroy matched word
        item.element.style.transform = 'scale(1.3)';
        item.element.style.opacity = '0';
        setTimeout(() => item.element.remove(), 150);

        this.words.splice(i, 1);
        this.score += 100;
        this.speed = Math.min(3.5, 1.0 + (this.score / 1500));
        this.updateHUD();

        if (window.typeforgeSound) window.typeforgeSound.playSuccess();

        this.input.value = '';
        return;
      }
    }
  }

  gameOver() {
    this.isRunning = false;
    cancelAnimationFrame(this.animationId);
    clearTimeout(this.spawnTimer);

    this.input.disabled = true;
    if (this.finalScoreDisplay) this.finalScoreDisplay.textContent = this.score;
    this.overlay.style.display = 'flex';
  }
}

window.FallingWordsGame = FallingWordsGame;
