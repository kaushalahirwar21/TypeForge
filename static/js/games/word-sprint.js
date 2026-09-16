/**
 * TypeForge Game 2: Word Sprint
 * 60-Second rapid fire typing sprint. Type as many words as possible!
 */

class WordSprintGame {
  constructor() {
    this.stage = document.getElementById('sprint-stage');
    this.targetWordDisplay = document.getElementById('sprint-target-word');
    this.upcomingWordsDisplay = document.getElementById('sprint-upcoming-words');
    this.timerDisplay = document.getElementById('sprint-timer');
    this.scoreDisplay = document.getElementById('sprint-score');
    this.input = document.getElementById('sprint-input');
    this.overlay = document.getElementById('sprint-overlay');
    this.finalScoreDisplay = document.getElementById('sprint-final-score');
    this.finalWpmDisplay = document.getElementById('sprint-final-wpm');
    this.restartBtn = document.getElementById('sprint-restart-btn');

    this.wordBank = [
      'journey', 'mountain', 'galaxy', 'quantum', 'rhythm', 'horizon', 'whisper',
      'crystal', 'freedom', 'glacier', 'gravity', 'velocity', 'thunder', 'dynamic',
      'eclipse', 'feather', 'diamond', 'harvest', 'illusion', 'justice', 'lantern',
      'miracle', 'nucleus', 'odyssey', 'pioneer', 'radiant', 'shelter', 'triumph',
      'universe', 'volcano', 'warrior', 'zenith', 'beacon', 'canyon', 'destiny'
    ];

    this.queue = [];
    this.score = 0;
    this.totalChars = 0;
    this.timeLeft = 60;
    this.timer = null;
    this.isRunning = false;

    this.init();
  }

  init() {
    if (!this.input) return;
    this.input.addEventListener('input', (e) => this.checkInput(e.target.value));
    if (this.restartBtn) {
      this.restartBtn.addEventListener('click', () => this.start());
    }
  }

  start() {
    this.reset();
    this.isRunning = true;
    this.overlay.style.display = 'none';
    this.input.disabled = false;
    this.input.value = '';
    this.input.focus();

    this.timer = setInterval(() => {
      this.timeLeft--;
      if (this.timerDisplay) this.timerDisplay.textContent = `${this.timeLeft}s`;

      if (this.timeLeft <= 0) {
        this.gameOver();
      }
    }, 1000);
  }

  reset() {
    this.isRunning = false;
    clearInterval(this.timer);
    this.score = 0;
    this.totalChars = 0;
    this.timeLeft = 60;

    // Fill queue
    this.queue = [];
    for (let i = 0; i < 10; i++) {
      this.queue.push(this.getRandomWord());
    }

    this.updateDisplay();
    if (this.timerDisplay) this.timerDisplay.textContent = '60s';
    if (this.scoreDisplay) this.scoreDisplay.textContent = '0';
  }

  getRandomWord() {
    return this.wordBank[Math.floor(Math.random() * this.wordBank.length)];
  }

  updateDisplay() {
    if (this.targetWordDisplay && this.queue.length > 0) {
      this.targetWordDisplay.textContent = this.queue[0];
    }
    if (this.upcomingWordsDisplay && this.queue.length > 1) {
      this.upcomingWordsDisplay.textContent = this.queue.slice(1, 5).join('   ');
    }
  }

  checkInput(val) {
    if (!this.isRunning || this.queue.length === 0) return;

    const currentTarget = this.queue[0];
    const trimmed = val.trim().toLowerCase();

    if (trimmed === currentTarget) {
      this.score++;
      this.totalChars += currentTarget.length;
      if (this.scoreDisplay) this.scoreDisplay.textContent = this.score;

      if (window.typeforgeSound) window.typeforgeSound.playClick();

      // Shift queue
      this.queue.shift();
      this.queue.push(this.getRandomWord());
      this.updateDisplay();
      this.input.value = '';
    }
  }

  gameOver() {
    this.isRunning = false;
    clearInterval(this.timer);
    this.input.disabled = true;

    const wpm = Math.round((this.totalChars / 5) / 1.0); // 1 minute
    if (this.finalScoreDisplay) this.finalScoreDisplay.textContent = `${this.score} words`;
    if (this.finalWpmDisplay) this.finalWpmDisplay.textContent = `${wpm} WPM`;

    if (window.typeforgeSound) window.typeforgeSound.playSuccess();
    this.overlay.style.display = 'flex';
  }
}

window.WordSprintGame = WordSprintGame;
