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

  // Modal & Guide Elements
  const keyIntroModal = document.getElementById('key-intro-modal');
  const btnStartGuidedPractice = document.getElementById('btn-start-guided-practice');
  const btnShowGuide = document.getElementById('btn-show-guide');
  const foundationModal = document.getElementById('foundation-modal');
  const btnPostureGuide = document.getElementById('btn-posture-guide');
  const btnCloseFoundation = document.getElementById('btn-close-foundation');

  // Real-Time Finger Discipline Warning
  const fingerWarningCallout = document.getElementById('finger-warning-callout');
  const fingerWarningText = document.getElementById('finger-warning-text');
  let warningTimer = null;

  // Completion Modal Elements
  const modalBackdrop = document.getElementById('result-modal-backdrop');
  const modalStatusPill = document.getElementById('modal-status-pill');
  const modalTitle = document.getElementById('modal-title');
  const modalSubtitle = document.getElementById('modal-subtitle');
  const modalWpm = document.getElementById('modal-wpm');
  const modalAcc = document.getElementById('modal-acc');
  const modalErr = document.getElementById('modal-err');
  const modalTime = document.getElementById('modal-time');
  const modalFeedbackText = document.getElementById('modal-feedback-text');
  const modalMissedKeysContainer = document.getElementById('modal-missed-keys-container');
  const modalMissedKeysList = document.getElementById('modal-missed-keys-list');
  const modalRecText = document.getElementById('modal-recommendation-text');
  const modalSkillLearned = document.getElementById('modal-skill-learned');
  const modalXpBanner = document.getElementById('modal-xp-banner');
  const modalXpText = document.getElementById('modal-xp-text');
  const starsContainer = document.getElementById('modal-stars-container');
  const nextLessonBtn = document.getElementById('modal-btn-next');
  const retryBtn = document.getElementById('modal-btn-retry');
  const modalBtnDrill = document.getElementById('modal-btn-drill');

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
    onFingerWarning: (expectedChar, mistakeCount) => {
      if (!fingerWarningCallout || !fingerWarningText) return;
      const mapping = keyboard.getMapping(expectedChar);
      const fingerName = mapping ? mapping.name : 'proper finger';
      const keyDisplay = expectedChar === ' ' ? 'SPACE' : expectedChar.toUpperCase();
      fingerWarningText.textContent = `Finger Warning: Use your ${fingerName} for "${keyDisplay}"! (${mistakeCount} misses)`;
      fingerWarningCallout.classList.add('show');
      if (warningTimer) clearTimeout(warningTimer);
      warningTimer = setTimeout(() => {
        fingerWarningCallout.classList.remove('show');
      }, 3500);
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

    // Populate Modal Stats
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

    // Provisional display while awaiting server confirmation
    if (stats.accuracy >= 90) {
      if (modalStatusPill) {
        modalStatusPill.className = 'mastery-pill status-mastered';
        modalStatusPill.innerHTML = 'Mastered 🏅';
      }
      modalTitle.textContent = "Lesson Mastered!";
      modalSubtitle.textContent = "Outstanding accuracy and clean touch-typing habits.";
      if (window.typeforgeSound) window.typeforgeSound.playSuccess();
    } else if (stats.accuracy >= minAcc) {
      if (modalStatusPill) {
        modalStatusPill.className = 'mastery-pill status-completed';
        modalStatusPill.innerHTML = 'Completed ✓';
      }
      modalTitle.textContent = "Lesson Completed";
      modalSubtitle.textContent = "Good progress! Reach 90%+ Accuracy to unlock Mastered status.";
      if (window.typeforgeSound) window.typeforgeSound.playSuccess();
    } else {
      if (modalStatusPill) {
        modalStatusPill.className = 'mastery-pill status-needs-practice';
        modalStatusPill.innerHTML = 'Practice Needed ⚠️';
      }
      modalTitle.textContent = "Practice Recommended";
      modalSubtitle.textContent = `Target accuracy is ${minAcc}%. Precision must come before speed.`;
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
        // Update Title & Subtitle from server
        if (data.title) modalTitle.textContent = data.title;
        if (data.feedback_msg) {
          modalSubtitle.textContent = data.feedback_msg;
          if (modalFeedbackText) modalFeedbackText.textContent = data.feedback_msg;
        }

        // Update Status Pill
        if (modalStatusPill && data.status) {
          modalStatusPill.className = 'mastery-pill';
          if (data.status === 'MASTERED') {
            modalStatusPill.classList.add('status-mastered');
            modalStatusPill.innerHTML = 'Mastered 🏅';
          } else if (data.status === 'COMPLETED') {
            modalStatusPill.classList.add('status-completed');
            modalStatusPill.innerHTML = 'Completed ✓';
          } else {
            modalStatusPill.classList.add('status-needs-practice');
            modalStatusPill.innerHTML = 'Practice Needed ⚠️';
          }
        }

        // Most Missed Keys & Drill Routing
        if (data.most_missed_keys && data.most_missed_keys.length > 0) {
          if (modalMissedKeysContainer && modalMissedKeysList) {
            modalMissedKeysContainer.style.display = 'block';
            modalMissedKeysList.innerHTML = '';
            data.most_missed_keys.forEach(item => {
              const tag = document.createElement('span');
              tag.className = 'missed-key-tag';
              tag.textContent = `${item.key} (${item.count} misses)`;
              modalMissedKeysList.appendChild(tag);
            });
          }
          if (modalBtnDrill) {
            const weakKeysParam = data.most_missed_keys.map(item => item.key.toLowerCase()).join(',');
            modalBtnDrill.href = `/practice/?keys=${encodeURIComponent(weakKeysParam)}`;
          }
        } else {
          if (modalMissedKeysContainer) modalMissedKeysContainer.style.display = 'none';
          if (modalBtnDrill) modalBtnDrill.href = '/practice/';
        }

        // Recommendation Text
        if (modalRecText && data.recommended_practice) {
          modalRecText.textContent = data.recommended_practice;
        }

        // Skill Learned
        if (modalSkillLearned && data.skill_learned) {
          modalSkillLearned.textContent = data.skill_learned;
        }

        // XP Banner
        if (data.xp_earned > 0 && modalXpBanner && modalXpText) {
          modalXpBanner.style.display = 'inline-flex';
          modalXpText.textContent = `+${data.xp_earned} XP Earned!`;
        }

        // Next Lesson Button (Enforces min_accuracy_threshold)
        if (data.unlocked_next && data.next_lesson_number && nextLessonBtn) {
          nextLessonBtn.style.display = 'inline-flex';
          nextLessonBtn.href = `/lesson/${data.next_lesson_number}/`;
        } else if (nextLessonBtn) {
          nextLessonBtn.style.display = 'none';
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

  // Teacher Intro Modal Handlers
  if (btnStartGuidedPractice && keyIntroModal) {
    btnStartGuidedPractice.addEventListener('click', () => {
      keyIntroModal.classList.remove('show');
      arenaCard.focus();
    });
  }

  if (btnShowGuide && keyIntroModal) {
    btnShowGuide.addEventListener('click', () => {
      keyIntroModal.classList.add('show');
    });
  }

  // Foundation & Posture Modal Handlers
  if (btnPostureGuide && foundationModal) {
    btnPostureGuide.addEventListener('click', () => {
      foundationModal.classList.add('show');
    });
  }

  if (btnCloseFoundation && foundationModal) {
    btnCloseFoundation.addEventListener('click', () => {
      foundationModal.classList.remove('show');
      arenaCard.focus();
    });
  }

  // Keyboard Event Routing
  window.addEventListener('keydown', (e) => {
    // If Teacher Intro Modal is open, Enter/Escape begins practice
    if (keyIntroModal && keyIntroModal.classList.contains('show')) {
      if (e.key === 'Enter' || e.key === 'Escape') {
        e.preventDefault();
        keyIntroModal.classList.remove('show');
        arenaCard.focus();
      }
      return;
    }

    // If Posture Modal is open, Enter/Escape closes it
    if (foundationModal && foundationModal.classList.contains('show')) {
      if (e.key === 'Enter' || e.key === 'Escape') {
        e.preventDefault();
        foundationModal.classList.remove('show');
        arenaCard.focus();
      }
      return;
    }

    // If result modal is open, ignore
    if (modalBackdrop && modalBackdrop.classList.contains('show')) return;

    // Remove focus overlay if user begins typing
    if (focusOverlay && focusOverlay.classList.contains('visible')) {
      focusOverlay.classList.remove('visible');
    }

    engine.handleKey(e);
  });

  // Focus Handling
  window.addEventListener('blur', () => {
    if (!engine.isCompleted && engine.isStarted) {
      if (focusOverlay) focusOverlay.classList.add('visible');
    }
  });

  if (focusOverlay) {
    focusOverlay.addEventListener('click', () => {
      focusOverlay.classList.remove('visible');
      arenaCard.focus();
    });
  }

  // Controls Handlers
  if (restartBtn) {
    restartBtn.addEventListener('click', () => {
      engine.reset();
      renderText();
      modalBackdrop.classList.remove('show');
      arenaCard.focus();
    });
  }

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
