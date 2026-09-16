/**
 * TypeForge Real-Time Typing Engine
 * High-performance, zero-latency keystroke processor and metrics calculator.
 */

class TypingEngine {
  constructor(targetText, options = {}) {
    this.targetText = targetText || '';
    this.targetLength = this.targetText.length;
    this.currentIndex = 0;

    // Timing
    this.startTime = null;
    this.endTime = null;
    this.elapsedSeconds = 0;
    this.timerInterval = null;

    // Counters
    this.totalTypedChars = 0;
    this.correctChars = 0;
    this.mistakesCount = 0;
    this.keyMistakes = {}; // { 'f': 2, 'j': 1 }

    // State
    this.isStarted = false;
    this.isCompleted = false;
    this.charStates = new Array(this.targetLength).fill('pending'); // 'pending', 'correct', 'incorrect'

    // Callbacks
    this.onCharTyped = options.onCharTyped || null;
    this.onProgress = options.onProgress || null;
    this.onComplete = options.onComplete || null;
    this.onMistake = options.onMistake || null;
  }

  startTimer() {
    if (this.isStarted) return;
    this.isStarted = true;
    this.startTime = performance.now();

    this.timerInterval = setInterval(() => {
      if (!this.isCompleted && this.startTime) {
        this.elapsedSeconds = (performance.now() - this.startTime) / 1000;
        this.dispatchProgress();
      }
    }, 150);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
    if (this.startTime && !this.endTime) {
      this.endTime = performance.now();
      this.elapsedSeconds = (this.endTime - this.startTime) / 1000;
    }
  }

  handleKey(e) {
    if (this.isCompleted) return;

    // Ignore standalone modifier keys
    if (['Shift', 'Control', 'Alt', 'Meta', 'CapsLock', 'Tab', 'Escape', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
      return;
    }

    // Start on first key
    if (!this.isStarted) {
      this.startTimer();
    }

    // Handle Backspace
    if (e.key === 'Backspace') {
      e.preventDefault();
      this.handleBackspace();
      return;
    }

    // Single character input
    if (e.key.length === 1) {
      e.preventDefault();
      this.handleCharacterInput(e.key);
    }
  }

  handleCharacterInput(inputChar) {
    if (this.currentIndex >= this.targetLength) return;

    const expectedChar = this.targetText[this.currentIndex];
    this.totalTypedChars++;

    if (inputChar === expectedChar) {
      // Correct keystroke
      this.charStates[this.currentIndex] = 'correct';
      this.correctChars++;
      this.currentIndex++;

      if (window.typeforgeSound) {
        window.typeforgeSound.playClick();
      }

      if (this.onCharTyped) {
        this.onCharTyped(this.currentIndex - 1, 'correct', expectedChar);
      }
    } else {
      // Mistake
      this.charStates[this.currentIndex] = 'incorrect';
      this.mistakesCount++;
      
      // Track mistake character
      const mistakeKey = expectedChar.toLowerCase();
      this.keyMistakes[mistakeKey] = (this.keyMistakes[mistakeKey] || 0) + 1;

      if (window.typeforgeSound) {
        window.typeforgeSound.playError();
      }

      if (this.onMistake) {
        this.onMistake(expectedChar, inputChar);
      }

      if (this.onCharTyped) {
        this.onCharTyped(this.currentIndex, 'incorrect', expectedChar);
      }
      // Advance so user doesn't get blocked permanently, but flag it
      this.currentIndex++;
    }

    this.dispatchProgress();

    // Check completion
    if (this.currentIndex >= this.targetLength) {
      this.complete();
    }
  }

  handleBackspace() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      const prevState = this.charStates[this.currentIndex];
      if (prevState === 'correct') {
        this.correctChars = Math.max(0, this.correctChars - 1);
      }
      this.charStates[this.currentIndex] = 'pending';

      if (window.typeforgeSound) {
        window.typeforgeSound.playClick();
      }

      if (this.onCharTyped) {
        this.onCharTyped(this.currentIndex, 'pending', this.targetText[this.currentIndex]);
      }

      this.dispatchProgress();
    }
  }

  calculateStats() {
    const elapsedMinutes = (this.elapsedSeconds || 0.1) / 60;

    // Standard WPM: (correct characters / 5) / minutes
    let wpm = (this.correctChars / 5) / elapsedMinutes;
    if (isNaN(wpm) || !isFinite(wpm) || wpm < 0) wpm = 0;

    // Raw WPM: (total characters / 5) / minutes
    let rawWpm = (this.totalTypedChars / 5) / elapsedMinutes;
    if (isNaN(rawWpm) || !isFinite(rawWpm) || rawWpm < 0) rawWpm = 0;

    // Accuracy: (correct characters / total typed characters) * 100
    let accuracy = 100;
    if (this.totalTypedChars > 0) {
      accuracy = (this.correctChars / this.totalTypedChars) * 100;
      if (isNaN(accuracy) || !isFinite(accuracy)) accuracy = 100;
      accuracy = Math.min(100, Math.max(0, accuracy));
    }

    const progressPercent = Math.min(100, (this.currentIndex / this.targetLength) * 100);

    return {
      wpm: Math.round(wpm),
      rawWpm: Math.round(rawWpm),
      accuracy: Math.round(accuracy),
      mistakesCount: this.mistakesCount,
      correctChars: this.correctChars,
      totalTypedChars: this.totalTypedChars,
      elapsedSeconds: Math.round(this.elapsedSeconds),
      progressPercent: Math.round(progressPercent),
      currentIndex: this.currentIndex,
      targetLength: this.targetLength,
      keyMistakes: this.keyMistakes,
    };
  }

  dispatchProgress() {
    if (this.onProgress) {
      this.onProgress(this.calculateStats());
    }
  }

  complete() {
    if (this.isCompleted) return;
    this.isCompleted = true;
    this.stopTimer();

    if (window.typeforgeSound) {
      window.typeforgeSound.playSuccess();
    }

    const finalStats = this.calculateStats();
    if (this.onComplete) {
      this.onComplete(finalStats);
    }
  }

  reset() {
    this.stopTimer();
    this.currentIndex = 0;
    this.startTime = null;
    this.endTime = null;
    this.elapsedSeconds = 0;
    this.totalTypedChars = 0;
    this.correctChars = 0;
    this.mistakesCount = 0;
    this.keyMistakes = {};
    this.isStarted = false;
    this.isCompleted = false;
    this.charStates = new Array(this.targetLength).fill('pending');
    this.dispatchProgress();
  }
}

window.TypingEngine = TypingEngine;
