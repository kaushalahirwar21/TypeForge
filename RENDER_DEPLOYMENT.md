# 🚀 TypeForge — Render Production Deployment Guide

This guide walks you through deploying the **TypeForge** touch-typing learning platform to **Render** with a production-ready **PostgreSQL** database, **Gunicorn** WSGI application server, and **WhiteNoise** static asset handling with Brotli/Gzip compression.

---

## 🏗 Architecture Overview

```
                          Internet / Users
                                 │
                                 ▼ (HTTPS)
                     Render Global Reverse Proxy
                    (SSL Termination & CDN Edge)
                                 │
                                 ▼
                     Gunicorn WSGI Application Server
                     (typeforge.wsgi:application)
                                 │
            ┌────────────────────┴────────────────────┐
            ▼                                         ▼
   Static Assets & UI Engine                 Django 5.x Backend
   WhiteNoise Storage + Cache                Business Logic & APIs
   (staticfiles/ with hash caching)                   │
                                                      ▼ (SSL)
                                            Render PostgreSQL
                                            (DATABASE_URL)
```

- **Runtime**: Python 3.11+
- **Application Server**: Gunicorn (`gunicorn typeforge.wsgi:application`)
- **Static Assets**: WhiteNoise (`CompressedManifestStaticFilesStorage`) with Brotli and Gzip compression
- **Database**: Managed PostgreSQL on Render (configured automatically via `DATABASE_URL`)
- **Security**: HTTPS redirect, HSTS, Secure Cookies, CSRF Trusted Origins, Clickjacking & XSS protections

---

## 📋 Prerequisites

1. A **GitHub account** with access to your repository:
   `https://github.com/kaushalahirwar21/TypeForge`
2. A free account on **[Render.com](https://render.com/)**.

---

## ⚡ Method 1: Automated Blueprint Deployment (Recommended)

TypeForge includes a `render.yaml` infrastructure-as-code Blueprint file in the root of the repository. This automatically provisions both the **Web Service** and the **PostgreSQL Database** in one click.

### Step 1: Push Changes to GitHub

Ensure all recent deployment changes are committed and pushed to GitHub:

```bash
git push origin master
```

### Step 2: Create Blueprint on Render

1. Log in to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** in the top right corner and select **Blueprint**.
3. Connect your GitHub repository: `kaushalahirwar21/TypeForge`.
4. Give your Blueprint instance a name (e.g., `typeforge`).
5. Render will detect the `render.yaml` specification and show the resources to create:
   - **Service**: `typeforge` (Web Service, Python runtime)
   - **Database**: `typeforge-db` (PostgreSQL database)
6. Click **Apply**.
7. Render will automatically:
   - Provision the PostgreSQL database.
   - Inject the `DATABASE_URL` and a generated `SECRET_KEY` into the Web Service.
   - Run `./build.sh` (installing dependencies, collecting static files, applying migrations, and seeding all 54 lessons).
   - Start the service using `gunicorn typeforge.wsgi:application`.

---

## 🛠 Method 2: Manual Step-by-Step Setup

If you prefer configuring resources manually in the Render UI:

### Step 1: Create a PostgreSQL Database on Render

1. On the Render Dashboard, click **New +** → **PostgreSQL**.
2. Configure database settings:
   - **Name**: `typeforge-db`
   - **Database**: `typeforge`
   - **User**: `typeforge_user`
   - **Region**: Choose the region closest to you (e.g., `Oregon (US West)` or `Frankfurt (EU)`)
   - **Plan**: `Free`
3. Click **Create Database**.
4. Wait for database provisioning to finish. Once ready, copy the **Internal Database URL** (e.g., `postgres://typeforge_user:...@dpg-...-a/typeforge`).

### Step 2: Create the Web Service

1. On the Render Dashboard, click **New +** → **Web Service**.
2. Select **Build and deploy from a Git repository** and pick `kaushalahirwar21/TypeForge`.
3. Configure the Web Service:
   - **Name**: `typeforge`
   - **Region**: Same region as your database (e.g., `Oregon (US West)`)
   - **Branch**: `master`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn typeforge.wsgi:application`
   - **Plan**: `Free`
4. Expand **Advanced** and configure the **Health Check Path**:
   - **Health Check Path**: `/health/`

### Step 3: Add Environment Variables

In the **Environment Variables** section of the Web Service, add the following key-value pairs:

| Variable | Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.11.8` | Sets standard Python 3.11 runtime |
| `DEBUG` | `False` | Disables debug mode in production |
| `SECRET_KEY` | *(Click "Generate" or provide a 50+ char random string)* | Production secret encryption key |
| `DATABASE_URL` | *(Paste Internal Database URL from Step 1)* | PostgreSQL connection URL |
| `ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` | Allowed hosts (Render subdomains) |
| `CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com` | Trusted origins for CSRF POST requests |
| `SECURE_SSL_REDIRECT` | `True` | Forces HTTPS redirection |

5. Click **Create Web Service**.

---

## 📦 What `build.sh` Does Automatically

During every deployment or git push, Render runs `./build.sh`:

```bash
#!/usr/bin/env bash
set -o errexit

# 1. Upgrade pip
python -m pip install --upgrade pip

# 2. Install all production packages (Django, Gunicorn, psycopg2, WhiteNoise, DRF)
pip install -r requirements.txt

# 3. Compile and hash static assets with WhiteNoise Brotli/Gzip compression
python manage.py collectstatic --no-input

# 4. Apply all schema migrations to PostgreSQL
python manage.py migrate

# 5. Populate full 54-lesson Touch Typing curriculum (idempotent)
python manage.py seed_curriculum
```

---

## 👤 Creating an Admin Superuser on Render

Once your service is deployed, create an administrative superuser:

1. In your Render Dashboard, go to your **`typeforge` Web Service**.
2. Click the **Shell** tab on the left menu (opens a terminal inside your live container).
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Enter your admin username, email, and password.
5. You can now log in at:
   `https://<your-service-name>.onrender.com/admin/`

---

## 🩺 Verifying Deployment & Health Check

### 1. Health Probe
Visit:
```
https://<your-service-name>.onrender.com/health/
```
Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "production"
}
```

### 2. Main Site
Visit:
```
https://<your-service-name>.onrender.com/
```
- Verify the landing page loads with CSS and SVG icons.
- Sign up for a new account or log in with your admin credentials.
- Open **Stage 1 / Lesson 1 (The F and J Guide Bumps)** to confirm interactive touch typing exercises load and function.
- Complete a lesson and verify XP and progress are saved to PostgreSQL.

---

## ⚠️ Important Production Notes

1. **Free Tier Inactivity (Spin-down)**:
   - On the Render Free tier, web services spin down after 15 minutes of inactivity. The first request after spin-down may take ~30-50 seconds to boot up.
2. **Ephemeral File System**:
   - Render containers have an ephemeral file system. TypeForge currently stores all assets (keyboard maps, hand SVGs, sounds, styling) in version-controlled static files. If you add user file/image upload fields in the future, integrate **Amazon S3** or **Cloudinary** using `django-storages`.
3. **Database Free Tier Lifetime**:
   - Render Free tier PostgreSQL databases expire after 30 days unless upgraded to a paid plan ($7/month). For permanent production data, upgrade the database or back up snapshots using `pg_dump`.

---

## 🛠 Local Development vs. Production Summary

| Component | Local Development | Production (Render) |
| :--- | :--- | :--- |
| **`DEBUG`** | `True` (via `.env`) | `False` |
| **Database** | SQLite (`db.sqlite3`) | Managed PostgreSQL (`DATABASE_URL`) |
| **Static Serving** | Django `runserver` | WhiteNoise (`CompressedManifestStaticFilesStorage`) |
| **Web Server** | Django Dev Server | Gunicorn (Multi-worker WSGI) |
| **Security** | Relaxed for localhost | HSTS, SSL Redirect, Secure Cookies, Strict Headers |
