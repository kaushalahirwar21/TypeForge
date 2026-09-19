# ⌨️ TypeRise — Learn Typing Faster

> **TypeRise is an interactive touch-typing platform that helps you build typing accuracy, speed, and confidence through guided progressive lessons, real-time finger posture guidance, arcade games, and rich analytics.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-18%20Passed-brightgreen.svg)]()

---

## 🚀 Key Highlights & Features

1. **Interactive Real-Time Typing Engine**
   - Zero-lag keystroke capture, character-by-character comparison.
   - Real-time calculations of Net WPM, Raw WPM, Accuracy %, errors, and elapsed time.
   - Dynamic cursor animations and non-blocking error handling.
   - Synthesized mechanical keyclick audio feedback using the native Web Audio API (zero external audio dependencies).

2. **Visual Virtual Keyboard & SVG Hand Guide**
   - Full QWERTY layout with color-coded finger mapping (Rose, Amber, Emerald, Royal Blue, Indigo, Cyan, Teal, Purple, Fuchsia).
   - Fluid responsive keyboard auto-scaling across viewports (from 320px small mobile to 1920px+ large desktop).
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
   - Leveling system (`Level = 1 + XP // 200`).
   - Daily practice streak counter with milestones.
   - 17 unique achievement badges across 5 categories (Lessons, Speed, Accuracy, Streaks, Volume).

8. **Weak Key Diagnostics Matrix**
   - Automatically tracks every character mistake across practice sessions.
   - Visual error matrix highlighting problematic keys.
   - Generates personalized warm-up and precision drill recommendations.

9. **Performance Analytics & SVG Charts**
   - Native SVG line charts tracking speed trajectory and accuracy curves over time.
   - Lifetime keystrokes and practice time metrics.

10. **Secure Authentication & 6-Digit Email OTP Lifecycle**
    - **Pending Inactive State**: New signups are safely created in `is_active=False` state until OTP is verified.
    - **10-Minute Expiry**: Verification codes automatically expire after 10 minutes.
    - **Brute-Force Protection**: OTPs are permanently locked out after 5 failed attempts.
    - **Rate Limiting**: 60-second cooldown between OTP requests.
    - **Direct Email Sending**: Reads configured credentials (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_HOST`, `EMAIL_PORT`) via standard Django SMTP.
    - **Render Free Tier Compatibility**: Built-in firewall detection with surfaced OTP helper in testing mode when cloud hosts block outbound SMTP port 587.

11. **Developer Profile**
    - Built-in Developer Profile showcasing creator **Kaushal Singh Ahirwar** with LinkedIn and Portfolio links.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Django 5.2, Django REST Framework
- **Database**: SQLite (default local development) / PostgreSQL (production via `dj-database-url`)
- **Frontend**: Semantic HTML5, Vanilla CSS3 (custom TypeRise design system, dark/slate/light themes), Vanilla ES6+ JavaScript
- **Audio**: Native Web Audio API synthesizer (no external audio files needed)
- **Static Assets**: WhiteNoise with Brotli & Gzip compression
- **Email Delivery**: Django SMTP (Gmail, custom SMTP) + Optional HTTPS API + Cloud firewall fallback

---

## 📦 Project Structure

```
TypeRise/
├── manage.py                     # Django CLI
├── requirements.txt              # Production dependencies
├── render.yaml                   # Infrastructure-as-code Blueprint (Web + PostgreSQL)
├── build.sh                      # Production build & static pipeline script
├── .env.example                  # Environment configuration template
├── typeforge/                    # Django project core configuration module
│   ├── settings.py               # Core settings (database, security, static, SMTP)
│   ├── urls.py                   # Master URL routing
│   ├── wsgi.py & asgi.py         # WSGI/ASGI entrypoints
├── core/                         # Main TypeRise application
│   ├── models.py                 # Course, Lesson, LessonProgress, TypingSession, EmailOTP, etc.
│   ├── email_service.py          # Secure OTP generator, rate limiter, SMTP dispatcher & fallback
│   ├── views.py                  # Page controllers, auth flows, and REST API endpoints
│   ├── urls.py                   # App routes
│   ├── forms.py                  # Signup, login, profile & settings forms
│   ├── admin.py                  # Django Admin integration
│   ├── context_processors.py     # Universal TypeRise branding & profile context
│   ├── tests.py                  # 18 automated unit tests (100% pass rate)
│   └── management/commands/
│       ├── seed_curriculum.py    # Populates all 13 levels, 54 lessons, and achievements
│       └── create_demo_user.py   # Seeds demo account with rich telemetry
├── static/
│   ├── css/
│   │   ├── base.css              # Global variables, typography, navigation, footer
│   │   ├── landing.css           # Landing page styling
│   │   ├── dashboard.css         # Dashboard widgets, telemetry cards, weak keys
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
│       ├── logo.svg              # TypeRise brand logo
│       └── developer.png         # Developer profile photo
└── templates/
    ├── base.html                 # Master layout
    ├── pages/                    # Landing, About, Developer, Help & FAQ
    ├── auth/                     # Signup, Login, Verify OTP, Reset Password OTP
    └── app/                      # Dashboard, Lessons, Typing Test, Games, etc.
```

---

## 🏁 Quickstart & How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/kaushalahirwar21/TypeRise.git
cd TypeRise
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

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

## 🔑 Pre-Configured Demo Account

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **Demo Typist** | `demo` | `Password123!` | `demo@typerise.local` |
| **Superuser / Admin** | `demo` | `Password123!` | Access at `/admin/` |

---

## 🧪 Running Automated Tests

TypeRise includes 18 comprehensive automated tests covering the typing engine, scoring, achievement rewards, OTP lifecycle (expiry, 5 failed attempts limit, cooldown), and auth flows:

```bash
python manage.py test core
```
```text
Ran 18 tests in 23.334s

OK
```

---

## 🌐 Production Deployment (Render)

1. Connect your repository (`kaushalahirwar21/TypeRise`) to **Render**.
2. Deploy using **Blueprint** (`render.yaml`) to automatically provision:
   - Web Service (`gunicorn typeforge.wsgi:application`)
   - PostgreSQL Database
3. Set your environment variables in Render:
   - `DEBUG`: `False`
   - `EMAIL_HOST`: `smtp.gmail.com`
   - `EMAIL_PORT`: `587`
   - `EMAIL_USE_TLS`: `True`
   - `EMAIL_HOST_USER`: `your-email@gmail.com`
   - `EMAIL_HOST_PASSWORD`: `your-16-char-app-password`
   - `DEFAULT_FROM_EMAIL`: `TypeRise <your-email@gmail.com>`
4. The deployment pipeline (`build.sh`) automatically runs migrations, collects static assets, and seeds lessons.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by **Kaushal Singh Ahirwar** (Creator & Developer of TypeRise).
