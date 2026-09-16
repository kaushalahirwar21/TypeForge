/**
 * TypeForge Lesson View Controller
 * Integrates TypingEngine, VirtualKeyboard, Sound, HUD, and Completion Modal
 */

document.addEventListener('DOMContentLoaded', () => {
  const lessonDataElem = document.getElementById('lesson-meta-data');
  if (!lessonDataElem) return;

  const lessonId = parseInt(lessonDataElem.dataset.lessonId, 10);
  const lessonNumber = parseInt(lessonDataElem.dataset.lessonNumber, 10);
  const targetText = lessonDataElem.dataset.targetText;
  const minWpm3 = parseInt(lessonDataElem.dataset.minWpm3 || 15, 10);
  const minWpm4 = parseInt(lessonDataElem.dataset.minWpm4 || 25, 10);
  const minWpm5 = parseInt(lessonDataElem.dataset.minWpm5 || 35, 10);
  const minAcc = parseFloat(lessonDataElem.dataset.minAcc || 85.0);

  // UI Elements
  const textDisplay = document.getElementById('typing-text-display');
  const wpmDisplay = document.getElementById('hud-wpm');
  const accDisplay = document.getElementById('hud-acc');
  const errDisplay = document.getElementById('hud-err');
  const timeDisplay = document.getElementById('hud-time');
  const progressBar = document.getElementById('lesson-progress-bar');
  const arenaCard = document.getElementById('typing-arena-card');
  const focusOverlay = document.getElementById('focus-overlay');
  const restartBtn = document.getElementById('btn-restart-lesson');
  const soundToggleBtn = document.getElementById('toggle-sound');
  const keyboardToggleBtn = document.getElementById('toggle-keyboard');
  const handGuideToggleBtn = document.getElementById('toggle-hand-guide');
  const keyboardSection = document.getElementById('virtual-keyboard');
  const handGuideSection = document.getElementById('hand-guide');

  // Modal Elements
  const modalBackdrop = document.getElementById('result-modal-backdrop');
  const modalTitle = document.getElementById('modal-title');
  const modalSubtitle = document.getElementById('modal-subtitle');
  const modalWpm = document.getElementById('modal-wpm');
  const modalAcc = document.getElementById('modal-acc');
  const modalErr = document.getElementById('modal-err');
  const modalTime = document.getElementById('modal-time');
  const modalXpBanner = document.getElementById('modal-xp-banner');
  const modalXpText = document.getElementById('modal-xp-text');
  const starsContainer = document.getElementById('modal-stars-container');
  const nextLessonBtn = document.getElementById('modal-btn-next');
  const retryBtn = document.getElementById('modal-btn-retry');

  // Initialize Virtual Keyboard & Finger Guide
  const keyboard = new TypeForgeKeyboard('virtual-keyboard', 'hand-guide');

  // Render Target Text Spans
  function renderText() {
    textDisplay.innerHTML = '';
    for (let i = 0; i < targetText.length; i++) {
      const span = document.createElement('span');
      span.className = 't-char pending';
      span.id = `char-${i}`;
      const ch = targetText[i];
      if (ch === ' ') {
        span.classList.add('space-char');
        span.textContent = ' ';
      } else {
        span.textContent = ch;
      }
      textDisplay.appendChild(span);
    }
    // Highlight first character
    updateCurrentCharHighlight(0);
  }

  function updateCurrentCharHighlight(index) {
    // Remove previous cursor
    const prevCurrent = textDisplay.querySelector('.t-char.current');
    if (prevCurrent) prevCurrent.classList.remove('current');

    if (index < targetText.length) {
      const nextCharSpan = document.getElementById(`char-${index}`);
      if (nextCharSpan) {
        nextCharSpan.classList.add('current');
      }
      keyboard.setTargetChar(targetText[index]);
    }
  }

  // Initialize Typing Engine
  const engine = new TypingEngine(targetText, {
    onCharTyped: (idx, state, expectedChar) => {
      const charSpan = document.getElementById(`char-${idx}`);
      if (charSpan) {
        charSpan.className = `t-char ${state}`;
        if (expectedChar === ' ') charSpan.classList.add('space-char');
      }
      updateCurrentCharHighlight(engine.currentIndex);
    },
    onProgress: (stats) => {
      wpmDisplay.textContent = stats.wpm;
      accDisplay.textContent = `${stats.accuracy}%`;
      errDisplay.textContent = stats.mistakesCount;
      const mins = Math.floor(stats.elapsedSeconds / 60);
      const secs = stats.elapsedSeconds % 60;
      timeDisplay.textContent = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
      progressBar.style.width = `${stats.progressPercent}%`;
    },
    onComplete: (finalStats) => {
      handleLessonComplete(finalStats);
    }
  });

  // Handle Lesson Completion & Rating
  function calculateStars(wpm, acc) {
    if (acc < minAcc) return 0;
    if (acc >= 98 && wpm >= minWpm5) return 5;
    if (acc >= 95 && wpm >= minWpm4) return 4;
    if (acc >= 90 && wpm >= minWpm3) return 3;
    if (acc >= 88) return 2;
    return 1;
  }

  function handleLessonComplete(stats) {
    const stars = calculateStars(stats.wpm, stats.accuracy);

    // Populate Modal
    modalWpm.textContent = stats.wpm;
    modalAcc.textContent = `${stats.accuracy}%`;
    modalErr.textContent = stats.mistakesCount;
    modalTime.textContent = `${stats.elapsedSeconds}s`;

    // Render Stars
    starsContainer.innerHTML = '';
    for (let i = 1; i <= 5; i++) {
      const star = document.createElement('span');
      star.className = `star-icon ${i <= stars ? 'filled' : ''}`;
      star.innerHTML = '★';
      starsContainer.appendChild(star);
    }

    if (stars >= 1) {
      modalTitle.textContent = stars >= 4 ? "Outstanding Typing!" : "Lesson Complete!";
      modalSubtitle.textContent = "You've successfully mastered this key progression.";
      if (nextLessonBtn) nextLessonBtn.style.display = 'inline-flex';
    } else {
      modalTitle.textContent = "Almost There!";
      modalSubtitle.textContent = `Target accuracy is ${minAcc}%. Keep practicing for high precision!`;
      if (nextLessonBtn) nextLessonBtn.style.display = 'none';
    }

    // Submit results to server via AJAX
    fetch('/api/lesson/submit/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        lesson_id: lessonId,
        wpm: stats.wpm,
        raw_wpm: stats.rawWpm,
        accuracy: stats.accuracy,
        mistakes_count: stats.mistakesCount,
        duration_seconds: stats.elapsedSeconds,
        characters_typed: stats.totalTypedChars,
        key_mistakes: stats.keyMistakes,
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        if (data.xp_earned > 0) {
          modalXpBanner.style.display = 'inline-flex';
          modalXpText.textContent = `+${data.xp_earned} XP Earned!`;
        }
        if (data.next_lesson_number && nextLessonBtn) {
          nextLessonBtn.href = `/lesson/${data.next_lesson_number}/`;
        }
        // If new achievements unlocked, notify
        if (data.new_achievements && data.new_achievements.length > 0) {
          data.new_achievements.forEach(ach => {
            showToastAchievement(ach.title, ach.description);
          });
        }
      }
    })
    .catch(err => console.error('Error submitting lesson:', err));

    modalBackdrop.classList.add('show');
  }

  function getCsrfToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || '';
  }

  function showToastAchievement(title, desc) {
    const toast = document.createElement('div');
    toast.className = 'alert alert-success';
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.innerHTML = `🏆 <strong>Achievement Unlocked!</strong> ${title} - ${desc}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 6000);
  }

  // Keyboard Event Routing
  window.addEventListener('keydown', (e) => {
    // If modal is open, ignore
    if (modalBackdrop.classList.contains('show')) return;

    // Remove focus overlay if user begins typing
    if (focusOverlay.classList.contains('visible')) {
      focusOverlay.classList.remove('visible');
    }

    engine.handleKey(e);
  });

  // Focus Handling
  window.addEventListener('blur', () => {
    if (!engine.isCompleted && engine.isStarted) {
      focusOverlay.classList.add('visible');
    }
  });

  focusOverlay.addEventListener('click', () => {
    focusOverlay.classList.remove('visible');
    arenaCard.focus();
  });

  // Controls Handlers
  restartBtn.addEventListener('click', () => {
    engine.reset();
    renderText();
    modalBackdrop.classList.remove('show');
    arenaCard.focus();
  });

  if (retryBtn) {
    retryBtn.addEventListener('click', () => {
      engine.reset();
      renderText();
      modalBackdrop.classList.remove('show');
      arenaCard.focus();
    });
  }

  soundToggleBtn.addEventListener('click', () => {
    const state = window.typeforgeSound.toggle();
    soundToggleBtn.classList.toggle('active', state);
    soundToggleBtn.querySelector('.hud-label').textContent = state ? 'Sound: On' : 'Sound: Off';
  });

  keyboardToggleBtn.addEventListener('click', () => {
    const isHidden = keyboardSection.classList.toggle('hidden-element');
    keyboardToggleBtn.classList.toggle('active', !isHidden);
  });

  handGuideToggleBtn.addEventListener('click', () => {
    const isHidden = handGuideSection.classList.toggle('hidden-element');
    handGuideToggleBtn.classList.toggle('active', !isHidden);
  });

  // Initial Boot
  renderText();
  arenaCard.focus();
});
