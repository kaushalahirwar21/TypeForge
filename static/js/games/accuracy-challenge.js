/**
 * TypeRise Game 3: Accuracy Challenge
 * Maintain 100% precision through a challenging passage. 3 strikes and out!
 */

class AccuracyChallengeGame {
  constructor() {
    this.stage = document.getElementById('accuracy-stage');
    this.passageElem = document.getElementById('accuracy-target-passage');
    this.livesDisplay = document.getElementById('accuracy-lives');
    this.scoreDisplay = document.getElementById('accuracy-score');
    this.overlay = document.getElementById('accuracy-overlay');
    this.finalTitle = document.getElementById('accuracy-final-title');
    this.finalDesc = document.getElementById('accuracy-final-desc');
    this.restartBtn = document.getElementById('accuracy-restart-btn');

    this.passages = [
      "Perfection is not attainable, but if we chase perfection we can catch excellence. Precision in typing demands complete presence of mind.",
      "The true master does not rush forward blindly, but strikes each key with quiet certainty and deliberate elegance.",
      "Every keystroke is an intentional craft. Build your velocity upon the unshakeable foundation of flawless accuracy."
    ];

    this.text = "";
    this.index = 0;
    this.lives = 3;
    this.score = 0;
    this.isRunning = false;

    this.init();
  }

  init() {
    if (this.restartBtn) {
      this.restartBtn.addEventListener('click', () => this.start());
    }

    window.addEventListener('keydown', (e) => {
      if (!this.isRunning) return;
      if (['Shift', 'Control', 'Alt', 'Meta', 'CapsLock', 'Tab'].includes(e.key)) return;

      if (e.key.length === 1) {
        e.preventDefault();
        this.handleChar(e.key);
      }
    });
  }

  start() {
    this.text = this.passages[Math.floor(Math.random() * this.passages.length)];
    this.index = 0;
    this.lives = 3;
    this.score = 0;
    this.isRunning = true;
    this.overlay.style.display = 'none';

    this.render();
    this.updateHUD();
  }

  render() {
    if (!this.passageElem) return;
    this.passageElem.innerHTML = '';
    for (let i = 0; i < this.text.length; i++) {
      const span = document.createElement('span');
      span.className = 't-char pending';
      span.id = `acc-char-${i}`;
      span.textContent = this.text[i];
      if (this.text[i] === ' ') span.classList.add('space-char');
      this.passageElem.appendChild(span);
    }
    this.highlight(0);
  }

  highlight(idx) {
    const prev = this.passageElem.querySelector('.t-char.current');
    if (prev) prev.classList.remove('current');

    if (idx < this.text.length) {
      const cur = document.getElementById(`acc-char-${idx}`);
      if (cur) cur.classList.add('current');
    }
  }

  updateHUD() {
    if (this.scoreDisplay) this.scoreDisplay.textContent = this.score;
    if (this.livesDisplay) {
      this.livesDisplay.innerHTML = '🛡️'.repeat(Math.max(0, this.lives)) + '❌'.repeat(Math.max(0, 3 - this.lives));
    }
  }

  handleChar(char) {
    if (this.index >= this.text.length) return;

    const expected = this.text[this.index];
    const span = document.getElementById(`acc-char-${this.index}`);

    if (char === expected) {
      span.className = 't-char correct';
      if (expected === ' ') span.classList.add('space-char');
      this.score += 10;
      this.index++;
      this.highlight(this.index);
      this.updateHUD();

      if (window.typeforgeSound) window.typeforgeSound.playClick();

      if (this.index >= this.text.length) {
        this.victory();
      }
    } else {
      span.className = 't-char incorrect';
      this.lives--;
      this.updateHUD();

      if (window.typeforgeSound) window.typeforgeSound.playError();

      if (this.lives <= 0) {
        this.gameOver();
      }
    }
  }

  victory() {
    this.isRunning = false;
    if (this.finalTitle) this.finalTitle.textContent = "Flawless Mastery!";
    if (this.finalDesc) this.finalDesc.textContent = `Completed passage with ${this.score} precision score and ${this.lives} shields remaining!`;
    if (window.typeforgeSound) window.typeforgeSound.playSuccess();
    this.overlay.style.display = 'flex';
  }

  gameOver() {
    this.isRunning = false;
    if (this.finalTitle) this.finalTitle.textContent = "Challenge Failed!";
    if (this.finalDesc) this.finalDesc.textContent = "You ran out of shields. Practice makes permanent!";
    this.overlay.style.display = 'flex';
  }
}

window.AccuracyChallengeGame = AccuracyChallengeGame;
