/**
 * TypeForge Timed Typing Test Controller
 * 30s, 60s, and 120s test modes with realistic prose paragraphs.
 */

document.addEventListener('DOMContentLoaded', () => {
  const PASSAGES = [
    "The art of typing with precision is built upon patient repetition and relaxed focus. As each finger learns its designated home on the keyboard, words flow effortlessly onto the screen. Speed is never forced; it is the natural consequence of accuracy and muscle memory working in perfect harmony.",
    "Technology continues to transform the way we communicate, work, and express ideas. From early mechanical typewriters with striking bars to modern digital interfaces, the keyboard remains our primary bridge between creative thoughts and the digital universe.",
    "In the quiet stillness of the early morning, crisp mountain air sweeps across the valley. Sunlight filters through the emerald canopy, illuminating winding forest trails and clear running streams where wildlife gathers in tranquil balance.",
    "Curiosity is the driving engine of scientific discovery. Throughout human history, inquisitive minds have looked at the stars, questioned the nature of reality, and engineered solutions that continuously expand our horizons.",
    "Effective software development requires clear communication, modular architecture, and thorough verification. Clean code is not just written for machines to execute, but for fellow engineers to read, maintain, and build upon for years to come."
  ];

  let selectedDuration = 60; // default 60s
  let timerInterval = null;
  let timeRemaining = 60;
  let testStarted = false;
  let testEnded = false;

  let testText = "";
  let currentIndex = 0;
  let correctCount = 0;
  let errorCount = 0;
  let totalKeystrokes = 0;

  // DOM Elements
  const durationBtns = document.querySelectorAll('.test-duration-btn');
  const timerDisplay = document.getElementById('test-timer-display');
  const wpmDisplay = document.getElementById('test-wpm-display');
  const accDisplay = document.getElementById('test-acc-display');
  const errDisplay = document.getElementById('test-err-display');
  const testArena = document.getElementById('test-arena');
  const textDisplay = document.getElementById('test-text-display');

  // Modal
  const modalBackdrop = document.getElementById('test-result-modal');
  const modalWpm = document.getElementById('test-res-wpm');
  const modalRawWpm = document.getElementById('test-res-raw');
  const modalAcc = document.getElementById('test-res-acc');
  const modalErrors = document.getElementById('test-res-err');
  const modalTotalChars = document.getElementById('test-res-total');
  const modalXpBanner = document.getElementById('test-xp-banner');
  const modalXpVal = document.getElementById('test-xp-val');
  const btnRetry = document.getElementById('test-btn-retry');
  const btnNewTest = document.getElementById('test-btn-new');

  // Select duration buttons
  durationBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (testStarted && !testEnded) return; // Prevent changing mid-test
      durationBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedDuration = parseInt(btn.dataset.duration, 10);
      resetTest();
    });
  });

  function getRandomPassage() {
    return PASSAGES[Math.floor(Math.random() * PASSAGES.length)];
  }

  function renderPassage() {
    textDisplay.innerHTML = '';
    testText = getRandomPassage();
    for (let i = 0; i < testText.length; i++) {
      const span = document.createElement('span');
      span.className = 't-char pending';
      span.id = `test-char-${i}`;
      if (testText[i] === ' ') {
        span.classList.add('space-char');
        span.textContent = ' ';
      } else {
        span.textContent = testText[i];
      }
      textDisplay.appendChild(span);
    }
    updateHighlight(0);
  }

  function updateHighlight(index) {
    const prev = textDisplay.querySelector('.t-char.current');
    if (prev) prev.classList.remove('current');

    if (index < testText.length) {
      const cur = document.getElementById(`test-char-${index}`);
      if (cur) cur.classList.add('current');
    }
  }

  function startTimer() {
    testStarted = true;
    timeRemaining = selectedDuration;
    timerInterval = setInterval(() => {
      timeRemaining--;
      timerDisplay.textContent = `${timeRemaining}s`;

      calculateMetrics();

      if (timeRemaining <= 0) {
        endTest();
      }
    }, 1000);
  }

  function calculateMetrics() {
    const elapsedSeconds = selectedDuration - timeRemaining;
    const elapsedMinutes = Math.max(0.016, elapsedSeconds / 60);

    const wpm = Math.round((correctCount / 5) / elapsedMinutes);
    const rawWpm = Math.round((totalKeystrokes / 5) / elapsedMinutes);
    const accuracy = totalKeystrokes > 0 ? Math.round((correctCount / totalKeystrokes) * 100) : 100;

    wpmDisplay.textContent = wpm;
    accDisplay.textContent = `${accuracy}%`;
    errDisplay.textContent = errorCount;

    return { wpm, rawWpm, accuracy };
  }

  function endTest() {
    clearInterval(timerInterval);
    testEnded = true;

    const { wpm, rawWpm, accuracy } = calculateMetrics();

    if (window.typeforgeSound) {
      window.typeforgeSound.playSuccess();
    }

    // Populate Modal
    modalWpm.textContent = wpm;
    modalRawWpm.textContent = rawWpm;
    modalAcc.textContent = `${accuracy}%`;
    modalErrors.textContent = errorCount;
    modalTotalChars.textContent = totalKeystrokes;

    // Save test result via API
    fetch('/api/test/submit/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        duration_mode: selectedDuration,
        wpm: wpm,
        raw_wpm: rawWpm,
        accuracy: accuracy,
        correct_chars: correctCount,
        incorrect_chars: errorCount,
        total_chars: totalKeystrokes,
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success && data.xp_earned > 0) {
        modalXpBanner.style.display = 'inline-flex';
        modalXpVal.textContent = `+${data.xp_earned} XP Earned!`;
      }
    })
    .catch(err => console.error('Error saving test:', err));

    modalBackdrop.classList.add('show');
  }

  function resetTest() {
    clearInterval(timerInterval);
    testStarted = false;
    testEnded = false;
    timeRemaining = selectedDuration;
    currentIndex = 0;
    correctCount = 0;
    errorCount = 0;
    totalKeystrokes = 0;

    timerDisplay.textContent = `${selectedDuration}s`;
    wpmDisplay.textContent = '0';
    accDisplay.textContent = '100%';
    errDisplay.textContent = '0';

    modalBackdrop.classList.remove('show');
    renderPassage();
    testArena.focus();
  }

  function getCsrfToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || '';
  }

  // Handle Keystrokes
  window.addEventListener('keydown', (e) => {
    if (modalBackdrop.classList.contains('show')) return;
    if (testEnded) return;

    if (['Shift', 'Control', 'Alt', 'Meta', 'CapsLock', 'Tab', 'Escape'].includes(e.key)) {
      return;
    }

    if (!testStarted) {
      startTimer();
    }

    if (e.key === 'Backspace') {
      e.preventDefault();
      if (currentIndex > 0) {
        currentIndex--;
        const charSpan = document.getElementById(`test-char-${currentIndex}`);
        if (charSpan.classList.contains('correct')) {
          correctCount = Math.max(0, correctCount - 1);
        }
        charSpan.className = 't-char pending';
        if (testText[currentIndex] === ' ') charSpan.classList.add('space-char');
        updateHighlight(currentIndex);
      }
      return;
    }

    if (e.key.length === 1) {
      e.preventDefault();
      totalKeystrokes++;
      const expected = testText[currentIndex];
      const charSpan = document.getElementById(`test-char-${currentIndex}`);

      if (e.key === expected) {
        correctCount++;
        charSpan.className = 't-char correct';
        if (window.typeforgeSound) window.typeforgeSound.playClick();
      } else {
        errorCount++;
        charSpan.className = 't-char incorrect';
        if (window.typeforgeSound) window.typeforgeSound.playError();
      }

      if (expected === ' ') charSpan.classList.add('space-char');

      currentIndex++;
      updateHighlight(currentIndex);

      // If finished passage before timer, reload next passage
      if (currentIndex >= testText.length) {
        renderPassage();
        currentIndex = 0;
      }
    }
  });

  btnRetry.addEventListener('click', resetTest);
  btnNewTest.addEventListener('click', resetTest);

  // Initialize
  resetTest();
});
