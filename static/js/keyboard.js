/**
 * TypeForge Virtual Keyboard & Finger Guide Coordinator
 * Accurately maps all characters, shifts, fingers and SVG vectors.
 */

const KEY_MAPPINGS = {
  // Number row
  '`': { code: 'Backquote', finger: 'l-pinky', name: 'Left Pinky' },
  '~': { code: 'Backquote', finger: 'l-pinky', name: 'Left Pinky', shift: 'r-shift' },
  '1': { code: 'Digit1', finger: 'l-pinky', name: 'Left Pinky' },
  '!': { code: 'Digit1', finger: 'l-pinky', name: 'Left Pinky', shift: 'r-shift' },
  '2': { code: 'Digit2', finger: 'l-ring', name: 'Left Ring' },
  '@': { code: 'Digit2', finger: 'l-ring', name: 'Left Ring', shift: 'r-shift' },
  '3': { code: 'Digit3', finger: 'l-mid', name: 'Left Middle' },
  '#': { code: 'Digit3', finger: 'l-mid', name: 'Left Middle', shift: 'r-shift' },
  '4': { code: 'Digit4', finger: 'l-index', name: 'Left Index' },
  '$': { code: 'Digit4', finger: 'l-index', name: 'Left Index', shift: 'r-shift' },
  '5': { code: 'Digit5', finger: 'l-index', name: 'Left Index' },
  '%': { code: 'Digit5', finger: 'l-index', name: 'Left Index', shift: 'r-shift' },
  '6': { code: 'Digit6', finger: 'r-index', name: 'Right Index' },
  '^': { code: 'Digit6', finger: 'r-index', name: 'Right Index', shift: 'l-shift' },
  '7': { code: 'Digit7', finger: 'r-index', name: 'Right Index' },
  '&': { code: 'Digit7', finger: 'r-index', name: 'Right Index', shift: 'l-shift' },
  '8': { code: 'Digit8', finger: 'r-mid', name: 'Right Middle' },
  '*': { code: 'Digit8', finger: 'r-mid', name: 'Right Middle', shift: 'l-shift' },
  '9': { code: 'Digit9', finger: 'r-ring', name: 'Right Ring' },
  '(': { code: 'Digit9', finger: 'r-ring', name: 'Right Ring', shift: 'l-shift' },
  '0': { code: 'Digit0', finger: 'r-pinky', name: 'Right Pinky' },
  ')': { code: 'Digit0', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },
  '-': { code: 'Minus', finger: 'r-pinky', name: 'Right Pinky' },
  '_': { code: 'Minus', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },
  '=': { code: 'Equal', finger: 'r-pinky', name: 'Right Pinky' },
  '+': { code: 'Equal', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },

  // Top QWERTY row
  'q': { code: 'KeyQ', finger: 'l-pinky', name: 'Left Pinky' },
  'Q': { code: 'KeyQ', finger: 'l-pinky', name: 'Left Pinky', shift: 'r-shift' },
  'w': { code: 'KeyW', finger: 'l-ring', name: 'Left Ring' },
  'W': { code: 'KeyW', finger: 'l-ring', name: 'Left Ring', shift: 'r-shift' },
  'e': { code: 'KeyE', finger: 'l-mid', name: 'Left Middle' },
  'E': { code: 'KeyE', finger: 'l-mid', name: 'Left Middle', shift: 'r-shift' },
  'r': { code: 'KeyR', finger: 'l-index', name: 'Left Index' },
  'R': { code: 'KeyR', finger: 'l-index', name: 'Left Index', shift: 'r-shift' },
  't': { code: 'KeyT', finger: 'l-index', name: 'Left Index' },
  'T': { code: 'KeyT', finger: 'l-index', name: 'Left Index', shift: 'r-shift' },
  'y': { code: 'KeyY', finger: 'r-index', name: 'Right Index' },
  'Y': { code: 'KeyY', finger: 'r-index', name: 'Right Index', shift: 'l-shift' },
  'u': { code: 'KeyU', finger: 'r-index', name: 'Right Index' },
  'U': { code: 'KeyU', finger: 'r-index', name: 'Right Index', shift: 'l-shift' },
  'i': { code: 'KeyI', finger: 'r-mid', name: 'Right Middle' },
  'I': { code: 'KeyI', finger: 'r-mid', name: 'Right Middle', shift: 'l-shift' },
  'o': { code: 'KeyO', finger: 'r-ring', name: 'Right Ring' },
  'O': { code: 'KeyO', finger: 'r-ring', name: 'Right Ring', shift: 'l-shift' },
  'p': { code: 'KeyP', finger: 'r-pinky', name: 'Right Pinky' },
  'P': { code: 'KeyP', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },
  '[': { code: 'BracketLeft', finger: 'r-pinky', name: 'Right Pinky' },
  '{': { code: 'BracketLeft', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },
  ']': { code: 'BracketRight', finger: 'r-pinky', name: 'Right Pinky' },
  '}': { code: 'BracketRight', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },
  '\\': { code: 'Backslash', finger: 'r-pinky', name: 'Right Pinky' },
  '|': { code: 'Backslash', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },

  // Home Row
  'a': { code: 'KeyA', finger: 'l-pinky', name: 'Left Pinky' },
  'A': { code: 'KeyA', finger: 'l-pinky', name: 'Left Pinky', shift: 'r-shift' },
  's': { code: 'KeyS', finger: 'l-ring', name: 'Left Ring' },
  'S': { code: 'KeyS', finger: 'l-ring', name: 'Left Ring', shift: 'r-shift' },
  'd': { code: 'KeyD', finger: 'l-mid', name: 'Left Middle' },
  'D': { code: 'KeyD', finger: 'l-mid', name: 'Left Middle', shift: 'r-shift' },
  'f': { code: 'KeyF', finger: 'l-index', name: 'Left Index' },
  'F': { code: 'KeyF', finger: 'l-index', name: 'Left Index', shift: 'r-shift' },
  'g': { code: 'KeyG', finger: 'l-index', name: 'Left Index' },
  'G': { code: 'KeyG', finger: 'l-index', name: 'Left Index', shift: 'r-shift' },
  'h': { code: 'KeyH', finger: 'r-index', name: 'Right Index' },
  'H': { code: 'KeyH', finger: 'r-index', name: 'Right Index', shift: 'l-shift' },
  'j': { code: 'KeyJ', finger: 'r-index', name: 'Right Index' },
  'J': { code: 'KeyJ', finger: 'r-index', name: 'Right Index', shift: 'l-shift' },
  'k': { code: 'KeyK', finger: 'r-mid', name: 'Right Middle' },
  'K': { code: 'KeyK', finger: 'r-mid', name: 'Right Middle', shift: 'l-shift' },
  'l': { code: 'KeyL', finger: 'r-ring', name: 'Right Ring' },
  'L': { code: 'KeyL', finger: 'r-ring', name: 'Right Ring', shift: 'l-shift' },
  ';': { code: 'Semicolon', finger: 'r-pinky', name: 'Right Pinky' },
  ':': { code: 'Semicolon', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },
  "'": { code: 'Quote', finger: 'r-pinky', name: 'Right Pinky' },
  '"': { code: 'Quote', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },

  // Bottom Row
  'z': { code: 'KeyZ', finger: 'l-pinky', name: 'Left Pinky' },
  'Z': { code: 'KeyZ', finger: 'l-pinky', name: 'Left Pinky', shift: 'r-shift' },
  'x': { code: 'KeyX', finger: 'l-ring', name: 'Left Ring' },
  'X': { code: 'KeyX', finger: 'l-ring', name: 'Left Ring', shift: 'r-shift' },
  'c': { code: 'KeyC', finger: 'l-mid', name: 'Left Middle' },
  'C': { code: 'KeyC', finger: 'l-mid', name: 'Left Middle', shift: 'r-shift' },
  'v': { code: 'KeyV', finger: 'l-index', name: 'Left Index' },
  'V': { code: 'KeyV', finger: 'l-index', name: 'Left Index', shift: 'r-shift' },
  'b': { code: 'KeyB', finger: 'l-index', name: 'Left Index' },
  'B': { code: 'KeyB', finger: 'l-index', name: 'Left Index', shift: 'r-shift' },
  'n': { code: 'KeyN', finger: 'r-index', name: 'Right Index' },
  'N': { code: 'KeyN', finger: 'r-index', name: 'Right Index', shift: 'l-shift' },
  'm': { code: 'KeyM', finger: 'r-index', name: 'Right Index' },
  'M': { code: 'KeyM', finger: 'r-index', name: 'Right Index', shift: 'l-shift' },
  ',': { code: 'Comma', finger: 'r-mid', name: 'Right Middle' },
  '<': { code: 'Comma', finger: 'r-mid', name: 'Right Middle', shift: 'l-shift' },
  '.': { code: 'Period', finger: 'r-ring', name: 'Right Ring' },
  '>': { code: 'Period', finger: 'r-ring', name: 'Right Ring', shift: 'l-shift' },
  '/': { code: 'Slash', finger: 'r-pinky', name: 'Right Pinky' },
  '?': { code: 'Slash', finger: 'r-pinky', name: 'Right Pinky', shift: 'l-shift' },

  // Space Bar
  ' ': { code: 'Space', finger: 'thumb', name: 'Thumb' },
};

class TypeForgeKeyboard {
  constructor(keyboardElemId = 'virtual-keyboard', handGuideElemId = 'hand-guide') {
    this.keyboardElem = document.getElementById(keyboardElemId);
    this.handGuideElem = document.getElementById(handGuideElemId);
    this.promptTextElem = document.getElementById('guide-instruction-text');
    this.currentCode = null;
    this.currentShiftCode = null;
    this.currentFinger = null;

    this.bindPhysicalEvents();
  }

  bindPhysicalEvents() {
    window.addEventListener('keydown', (e) => {
      this.handlePhysicalKey(e.code, true);
    });
    window.addEventListener('keyup', (e) => {
      this.handlePhysicalKey(e.code, false);
    });
  }

  handlePhysicalKey(code, isPressed) {
    if (!this.keyboardElem) return;
    const keyElem = this.keyboardElem.querySelector(`[data-code="${code}"]`);
    if (keyElem) {
      if (isPressed) {
        keyElem.classList.add('key-pressed');
      } else {
        keyElem.classList.remove('key-pressed');
      }
    }
  }

  setTargetChar(char) {
    if (!char) return;
    const mapping = KEY_MAPPINGS[char];
    if (!mapping) return;

    // Reset previous target keys
    if (this.keyboardElem) {
      this.keyboardElem.querySelectorAll('.key-target').forEach(el => el.classList.remove('key-target'));
    }

    // Reset previous finger highlights
    if (this.handGuideElem) {
      this.handGuideElem.querySelectorAll('.finger-active').forEach(el => el.classList.remove('finger-active'));
    }

    // Highlight target key
    if (this.keyboardElem) {
      const targetKey = this.keyboardElem.querySelector(`[data-code="${mapping.code}"]`);
      if (targetKey) {
        targetKey.classList.add('key-target');
      }

      // If shifted, also highlight Shift key
      if (mapping.shift) {
        const shiftCode = mapping.shift === 'l-shift' ? 'ShiftLeft' : 'ShiftRight';
        const shiftKey = this.keyboardElem.querySelector(`[data-code="${shiftCode}"]`);
        if (shiftKey) {
          shiftKey.classList.add('key-target');
        }
      }
    }

    // Highlight active finger in SVG Hand Diagram
    if (this.handGuideElem && mapping.finger) {
      const fingerElems = this.handGuideElem.querySelectorAll(`[data-finger="${mapping.finger}"]`);
      fingerElems.forEach(el => el.classList.add('finger-active'));
    }

    // Update instruction text
    if (this.promptTextElem) {
      const keyDisplay = char === ' ' ? 'SPACE' : char.toUpperCase();
      let shiftNote = mapping.shift ? ` (+ ${mapping.shift === 'l-shift' ? 'LEFT' : 'RIGHT'} SHIFT)` : '';
      this.promptTextElem.innerHTML = `Press <span class="finger-name">${keyDisplay}${shiftNote}</span> with your <span class="finger-name">${mapping.name}</span>`;
    }
  }

  getMapping(char) {
    return KEY_MAPPINGS[char] || null;
  }
}

window.KEY_MAPPINGS = KEY_MAPPINGS;
window.TypeForgeKeyboard = TypeForgeKeyboard;

