# ⌨️ TypeForge — Professional Touch Typing Learning Platform

> **Master Touch Typing with Precision, Muscle Memory & Velocity**

TypeForge is a complete, commercial-grade, full-stack touch typing platform inspired by the learning architecture of TypingClub. It is built from the ground up with 100% original branding, modern UI design, structured progressive curriculum, interactive SVG finger guidance, zero-latency typing engine, arcade typing games, gamification, and detailed analytics.

---

## 🚀 Key Highlights & Features

1. **Interactive Real-Time Typing Engine**
   - Zero-lag keystroke capture, character-by-character comparison.
   - Real-time calculations of Net WPM, Raw WPM, Accuracy %, errors, and elapsed time.
   - Dynamic cursor animations and non-blocking error handling.
   - Synthesized mechanical keyclick audio feedback using the native Web Audio API (zero external audio dependencies).

2. **Visual Virtual Keyboard & SVG Hand Guide**
   - Full QWERTY layout with color-coded finger mapping (Rose, Amber, Emerald, Royal Blue, Indigo, Cyan, Teal, Purple, Fuchsia).
   - Real-time active key and Shift-key illumination.
   - Dual-hand vector SVG diagram highlighting the exact finger to use for every stroke.
   - Dynamic prompt banner: *"Use your LEFT INDEX finger on F"*.

3. **13-Level Progressive Curriculum (54 Complete Lessons)**
   - **Level 1**: Getting Started (F and J bumps, home row anchor, thumbs on Space)
   - **Level 2**: Home Row Mastery (D, K, S, L, A, Semicolon, home row words)
   - **Level 3**: Top Row (G, H, R, U, E, I, W, O, Q, P)
   - **Level 4**: Bottom Row (V, M, C, comma, X, period, Z, slash)
   - **Level 5**: Full Alphabet Integration (pangrams and flow)
   - **Level 6**: Capital Letters & Shift Keys (left/right shift coordination)
   - **Level 7**: Numbers Row (1–5 left hand, 6–0 right hand)
   - **Level 8**: Symbols & Punctuation (!, ?, ", ', brackets, math symbols)
   - **Level 9**: High-Frequency Common Words (Top 100 English words)
   - **Level 10**: Sentences & Flow (prose cadence and dialogue)
   - **Level 11**: Paragraphs & Literature (sustained long-form texts)
   - **Level 12**: Speed Sprints (velocity training for 60–80+ WPM)
   - **Level 13**: Precision Mastery (zero-mistake challenge & capstone graduation)

4. **1-5 Star Scoring & Sequential Unlocking**
   - Dynamic star algorithm based on WPM speed thresholds and accuracy percentage.
   - Automatic lesson unlocking upon achieving at least 1 star.

5. **Timed Typing Speed Test**
   - 30-second, 60-second, and 120-second modes.
   - Live countdown timer, realistic English prose passages.
   - Detailed completion breakdown (Net WPM, Raw WPM, Accuracy, Errors, Total keystrokes).
   - Automatic persistence for authenticated typists.

6. **Interactive Arcade Typing Games Suite**
   - **Falling Words**: Defend the baseline from descending word bubbles before they breach the danger line.
   - **Word Sprint**: 60-second high-intensity word sprint with live counter and WPM report.
   - **Accuracy Challenge**: Precision gauntlet where typing errors consume protective shields (3 strikes and out).

7. **Gamification & Habit Building**
   - Leveling system (Level = 1 + XP // 200).
   - Daily practice streak counter with milestones.
   - 17 unique achievement badges across 5 categories (Lessons, Speed, Accuracy, Streaks, Volume).

8. **Weak Key Diagnostics Matrix**
   - Automatically tracks every character mistake across practice sessions.
   - Visual error matrix highlighting problematic keys.
   - Generates personalized warm-up and precision drill recommendations.

9. **Performance Analytics & Charts**
   - Native SVG line charts tracking speed trajectory and accuracy curves over time.
   - Lifetime keystrokes and practice time metrics.

10. **Full User Authentication & Settings**
    - Secure registration, login (username or email), password reset, and profile management.
    - Custom user settings: toggle sound effects, toggle virtual keyboard, toggle hand guide, select font size, and choose themes.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, Django 5.2, Django REST Framework
- **Database**: SQLite (default zero-config local), PostgreSQL compatible via `dj-database-url`
- **Frontend**: Semantic HTML5, Vanilla CSS3 (custom TypeForge design system, dark/light themes), Vanilla ES6+ JavaScript
- **Audio**: Native Web Audio API synthesizer
- **Static Files**: WhiteNoise

---

## 📦 Project Structure

```
typing/
├── manage.py                     # Django CLI
├── requirements.txt              # Dependencies
├── .env.example                  # Environment configuration template
├── typeforge/                    # Django project configuration
│   ├── settings.py               # Core settings (SQLite/Postgres, Whitenoise, DRF)
│   ├── urls.py                   # Master URL routing
│   ├── wsgi.py & asgi.py
├── core/                         # Main TypeForge application
│   ├── models.py                 # Course, Lesson, LessonProgress, TypingSession, etc.
│   ├── views.py                  # Page view controllers & REST API endpoints
│   ├── urls.py                   # App routes
│   ├── forms.py                  # Registration, login, profile & settings forms
│   ├── admin.py                  # Comprehensive Django Admin integration
│   ├── context_processors.py     # Universal branding & profile context
│   ├── tests.py                  # Automated test suite (8 tests)
│   └── management/commands/
│       ├── seed_curriculum.py    # Populates all 13 levels, 54 lessons, and achievements
│       └── create_demo_user.py   # Seeds demo account with rich telemetry
├── static/
│   ├── css/
│   │   ├── base.css              # Global variables, typography, navigation, footer
│   │   ├── landing.css           # Marketing landing page styling
│   │   ├── dashboard.css         # Dashboard widgets, stats cards, weak keys
│   │   ├── lesson.css            # Typing arena, virtual keyboard, SVG hand guide
│   │   └── games.css             # Arcade games styling
│   ├── js/
│   │   ├── sound.js              # Web Audio API sound synthesizer
│   │   ├── keyboard.js           # Virtual keyboard & SVG hand guide coordinator
│   │   ├── typing-engine.js      # Zero-latency core typing engine
│   │   ├── lesson-view.js        # Lesson runner and completion modal controller
│   │   ├── typing-test.js        # Timed typing test coordinator
│   │   ├── charts.js             # SVG performance charts generator
│   │   └── games/
│   │       ├── falling-words.js
│   │       ├── word-sprint.js
│   │       └── accuracy-challenge.js
│   └── img/
│       └── logo.svg              # TypeForge brand logo
└── templates/
    ├── base.html                 # Main master layout
    ├── pages/                    # Landing, About, Help & FAQ
    ├── auth/                     # Signup, Login, Password Reset
    └── app/                      # Dashboard, Lessons, Typing Test, Games, etc.
```

---

## 🏁 Quickstart & How to Run Locally

### 1. Clone or Open Workspace
```bash
cd c:\Users\HP5CD\OneDrive\Documents\My_Projects\typing
```

### 2. Install Dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### 3. Run Migrations & Seed Data
```bash
python manage.py migrate
python manage.py seed_curriculum
python manage.py create_demo_user
```

### 4. Start Development Server
```bash
python manage.py runserver 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

## 🔑 Pre-Configured Test Accounts

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **Demo User** | `demo` | `Password123!` | `demo@typeforge.local` |
| **Admin Panel** | `demo` (superuser) | `Password123!` | Access at `/admin/` |

---

## 🧪 Running Automated Tests

TypeForge includes a comprehensive test suite covering models, authentication, star calculations, lesson unlocking, and typing test logging:

```bash
python manage.py test core
```
*Expected Output: `Ran 8 tests ... OK`*

---

## 🌐 Production Deployment Guide

1. Set `DEBUG=False` in your `.env` file.
2. Set a secure `SECRET_KEY` and specify `ALLOWED_HOSTS`.
3. Provide PostgreSQL database connection string via `DATABASE_URL`:
   ```env
   DATABASE_URL=postgres://user:password@host:5432/typeforge_db
   ```
4. Collect static assets:
   ```bash
   python manage.py collectstatic --noinput
   ```
5. Run using an ASGI/WSGI production server such as Gunicorn:
   ```bash
   gunicorn typeforge.wsgi:application --bind 0.0.0.0:8000
   ```
