import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg, Max, Sum, Count
from django.utils import timezone
import datetime

from .models import (
    UserProfile, UserSettings, Course, Lesson, LessonProgress,
    TypingSession, TypingTestResult, Achievement, UserAchievement, DailyActivity,
    EmailOTP
)
from .forms import SignUpForm, CustomLoginForm, ProfileEditForm, UserSettingsForm
from .email_service import create_and_send_otp, verify_otp_code


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    total_lessons = Lesson.objects.count()
    total_typists = User.objects.count() + 1420  # Friendly active community base
    return render(request, 'pages/landing.html', {
        'total_lessons': total_lessons,
        'total_typists': total_typists,
    })


def about(request):
    return render(request, 'pages/about.html')


def developer_view(request):
    return render(request, 'pages/developer.html')


def help_faq(request):
    return render(request, 'pages/help.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create user in pending / unverified state (is_active=False)
            user = form.save(commit=True)
            email = user.email
            name = f"{user.first_name} {user.last_name}".strip() or user.username

            # Dispatch OTP email using configured email account
            success, msg = create_and_send_otp(email, EmailOTP.PURPOSE_SIGNUP, user_name=name)
            if success:
                request.session['pending_signup_email'] = email
                request.session['pending_signup_name'] = name
                messages.success(request, f"A 6-digit verification code has been sent to {email}. Enter it below to activate your account.")
                return redirect('verify_otp')
            else:
                if "cooldown" in msg.lower() or "wait" in msg.lower():
                    messages.warning(request, msg)
                    request.session['pending_signup_email'] = email
                    request.session['pending_signup_name'] = name
                    return redirect('verify_otp')
                else:
                    messages.error(request, "Unable to send the email right now. Please try again later.")
    else:
        form = SignUpForm()
    
    return render(request, 'auth/signup.html', {'form': form})


def verify_otp_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    email = request.session.get('pending_signup_email')
    if not email and 'pending_signup' in request.session:
        email = request.session.get('pending_signup', {}).get('email')

    if not email:
        messages.warning(request, "No pending registration found. Please fill out the sign up form first.")
        return redirect('signup')

    user = User.objects.filter(email__iexact=email).first()
    name = (f"{user.first_name} {user.last_name}".strip() if user else None) or request.session.get('pending_signup_name', '')

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        if not otp_code and 'digit1' in request.POST:
            otp_code = ''.join([request.POST.get(f'digit{i}', '').strip() for i in range(1, 7)])

        is_valid, msg = verify_otp_code(email, otp_code, EmailOTP.PURPOSE_SIGNUP)
        if is_valid:
            if not user:
                messages.error(request, "Account not found. Please register again.")
                return redirect('signup')

            # Activate / verify account
            user.is_active = True
            user.save(update_fields=['is_active'])

            # Initialize Lesson 1 as unlocked
            first_lesson = Lesson.objects.order_by('level_number', 'lesson_number').first()
            if first_lesson:
                LessonProgress.objects.get_or_create(
                    user=user,
                    lesson=first_lesson,
                    defaults={'unlocked': True}
                )

            # Clean session
            request.session.pop('pending_signup_email', None)
            request.session.pop('pending_signup_name', None)
            request.session.pop('pending_signup', None)

            # Log in the newly activated user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, f"Welcome to TypeRise, {user.first_name or user.username}! Your email has been verified successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, msg)

    return render(request, 'auth/verify_otp.html', {
        'email': email,
        'name': name,
    })


def resend_otp_view(request):
    purpose = request.GET.get('purpose', 'signup')
    if purpose == 'forgot_password':
        email = request.session.get('reset_password_email')
        user = User.objects.filter(email__iexact=email).first() if email else None
        name = (user.first_name or user.username) if user else "Typist"
        redirect_url = 'reset_password_otp'
    else:
        email = request.session.get('pending_signup_email')
        if not email and 'pending_signup' in request.session:
            email = request.session.get('pending_signup', {}).get('email')
        user = User.objects.filter(email__iexact=email).first() if email else None
        name = (user.first_name or user.username) if user else request.session.get('pending_signup_name', 'Typist')
        redirect_url = 'verify_otp'

    if not email:
        messages.error(request, "Session expired. Please start the process again.")
        return redirect('signup' if purpose == 'signup' else 'forgot_password')

    success, msg = create_and_send_otp(email, purpose, user_name=name)
    if success:
        messages.success(request, f"A fresh 6-digit verification code has been dispatched to {email}.")
    else:
        if "cooldown" in msg.lower() or "wait" in msg.lower():
            messages.warning(request, msg)
        else:
            messages.error(request, "Unable to send the email right now. Please try again later.")

    return redirect(redirect_url)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Update user streak
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.update_streak()
            profile.save()
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            # Check if user entered email or username with pending verification
            entered_id = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            user_obj = (
                User.objects.filter(email__iexact=entered_id).first() or
                User.objects.filter(username__iexact=entered_id).first()
            )
            if user_obj and user_obj.check_password(password):
                if not user_obj.is_active:
                    request.session['pending_signup_email'] = user_obj.email
                    messages.warning(request, "Your account is pending verification. Please verify your email using the OTP.")
                    return redirect('verify_otp')
                else:
                    user_obj.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user_obj)
                    profile, _ = UserProfile.objects.get_or_create(user=user_obj)
                    profile.update_streak()
                    profile.save()
                    messages.success(request, f"Welcome back, {user_obj.first_name or user_obj.username}!")
                    next_url = request.GET.get('next') or 'dashboard'
                    return redirect(next_url)
            messages.error(request, "Invalid username or password. Please check and try again.")
    else:
        form = CustomLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. Keep up the great typing practice!")
    return redirect('landing')


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email:
            messages.error(request, "Please enter your registered email address.")
            return render(request, 'auth/forgot_password.html')

        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            success, msg = create_and_send_otp(
                email=user.email,
                purpose=EmailOTP.PURPOSE_FORGOT_PASSWORD,
                user_name=user.first_name or user.username
            )
            if success:
                request.session['reset_password_email'] = user.email
                messages.success(request, f"A 6-digit password reset code has been sent to {user.email}.")
                return redirect('reset_password_otp')
            else:
                if "cooldown" in msg.lower() or "wait" in msg.lower():
                    messages.warning(request, msg)
                    request.session['reset_password_email'] = user.email
                    return redirect('reset_password_otp')
                else:
                    messages.error(request, "Unable to send the email right now. Please try again later.")
        else:
            inactive_user = User.objects.filter(email__iexact=email, is_active=False).first()
            if inactive_user:
                messages.error(request, "This account is not activated yet. Please complete email verification first.")
            else:
                messages.error(request, "No registered account found with that email address.")

    return render(request, 'auth/forgot_password.html')


def reset_password_otp_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    email = request.session.get('reset_password_email')
    if not email:
        messages.warning(request, "Password reset session expired. Please enter your email again.")
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not new_password or len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'auth/reset_password_otp.html', {'email': email})

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match. Please re-enter.")
            return render(request, 'auth/reset_password_otp.html', {'email': email})

        is_valid, msg = verify_otp_code(email, otp_code, EmailOTP.PURPOSE_FORGOT_PASSWORD)
        if is_valid:
            user = User.objects.filter(email__iexact=email).first()
            if user:
                user.set_password(new_password)
                user.is_active = True
                user.save()
                request.session.pop('reset_password_email', None)
                messages.success(request, "Your password has been reset successfully! You can now log in with your new password.")
                return redirect('login')
            else:
                messages.error(request, "User account not found.")
        else:
            messages.error(request, msg)

    return render(request, 'auth/reset_password_otp.html', {'email': email})


def reset_password_done_view(request):
    return render(request, 'auth/reset_password_done.html')


@login_required
def dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Ensure first lesson is unlocked for new user
    first_lesson = Lesson.objects.order_by('level_number', 'lesson_number').first()
    if first_lesson:
        LessonProgress.objects.get_or_create(
            user=user,
            lesson=first_lesson,
            defaults={'unlocked': True}
        )

    # Calculate overall course progress
    total_lessons_count = Lesson.objects.count()
    completed_progresses = LessonProgress.objects.filter(user=user, completed=True)
    completed_count = completed_progresses.count()
    progress_percentage = int((completed_count / total_lessons_count * 100)) if total_lessons_count > 0 else 0

    # Determine current / next lesson to continue
    next_uncompleted = LessonProgress.objects.filter(
        user=user, unlocked=True, completed=False
    ).select_related('lesson').order_by('lesson__level_number', 'lesson__lesson_number').first()

    if next_uncompleted:
        current_lesson = next_uncompleted.lesson
    else:
        # If all unlocked are completed, find next lesson in order
        last_completed = completed_progresses.select_related('lesson').order_by('-lesson__lesson_number').first()
        if last_completed:
            current_lesson = Lesson.objects.filter(lesson_number__gt=last_completed.lesson.lesson_number).first() or last_completed.lesson
        else:
            current_lesson = first_lesson

    # Aggregate Typing Stats
    sessions = TypingSession.objects.filter(user=user)
    avg_wpm = sessions.aggregate(Avg('wpm'))['wpm__avg'] or 0.0
    best_wpm = sessions.aggregate(Max('wpm'))['wpm__max'] or 0.0
    avg_accuracy = sessions.aggregate(Avg('accuracy'))['accuracy__avg'] or 0.0
    recent_sessions = sessions.select_related('lesson')[:8]

    # Practice time in minutes/hours
    total_seconds = profile.total_practice_time_seconds
    practice_minutes = total_seconds // 60
    practice_hours = round(total_seconds / 3600.0, 1)

    # Weak Keys Analysis across last 25 sessions
    weak_keys_dict = {}
    for s in sessions[:25]:
        if s.key_mistakes and isinstance(s.key_mistakes, dict):
            for char, count in s.key_mistakes.items():
                weak_keys_dict[char] = weak_keys_dict.get(char, 0) + int(count)

    sorted_weak_keys = sorted(weak_keys_dict.items(), key=lambda item: item[1], reverse=True)[:6]
    weak_keys_list = [{'key': k, 'count': v} for k, v in sorted_weak_keys]

    # Recent Achievements
    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')[:5]
    mastered_count = LessonProgress.objects.filter(user=user, is_mastered=True).count()

    return render(request, 'app/dashboard.html', {
        'profile': profile,
        'total_lessons_count': total_lessons_count,
        'completed_count': completed_count,
        'mastered_count': mastered_count,
        'progress_percentage': progress_percentage,
        'current_lesson': current_lesson,
        'avg_wpm': round(avg_wpm, 1),
        'best_wpm': round(best_wpm, 1),
        'avg_accuracy': round(avg_accuracy, 1),
        'practice_minutes': practice_minutes,
        'practice_hours': practice_hours,
        'recent_sessions': recent_sessions,
        'weak_keys': weak_keys_list,
        'recent_achievements': user_achievements,
    })


@login_required
def course_map(request):
    user = request.user
    # Ensure first lesson is unlocked
    first_lesson = Lesson.objects.order_by('level_number', 'lesson_number').first()
    if first_lesson:
        LessonProgress.objects.get_or_create(user=user, lesson=first_lesson, defaults={'unlocked': True})

    lessons = Lesson.objects.all().order_by('level_number', 'lesson_number')
    user_progress_map = {
        p.lesson_id: p for p in LessonProgress.objects.filter(user=user)
    }

    # Group lessons by level
    levels_dict = {}
    for lesson in lessons:
        lvl_num = lesson.level_number
        if lvl_num not in levels_dict:
            levels_dict[lvl_num] = {
                'level_number': lvl_num,
                'level_title': lesson.level_title,
                'lessons': []
            }
        progress = user_progress_map.get(lesson.id)
        is_unlocked = progress.unlocked if progress else False
        is_completed = progress.completed if progress else False
        is_mastered = progress.is_mastered if progress else False
        stars = progress.stars if progress else 0
        best_wpm = progress.best_wpm if progress else 0.0

        levels_dict[lvl_num]['lessons'].append({
            'lesson': lesson,
            'is_unlocked': is_unlocked,
            'is_completed': is_completed,
            'is_mastered': is_mastered,
            'stars': stars,
            'best_wpm': round(best_wpm, 1),
        })

    levels_list = sorted(levels_dict.values(), key=lambda x: x['level_number'])
    
    # Count totals
    total_lessons = lessons.count()
    completed_count = sum(1 for p in user_progress_map.values() if p.completed)
    mastered_count = sum(1 for p in user_progress_map.values() if p.is_mastered)
    total_stars = sum(p.stars for p in user_progress_map.values())

    return render(request, 'app/course_map.html', {
        'levels': levels_list,
        'total_lessons': total_lessons,
        'completed_count': completed_count,
        'mastered_count': mastered_count,
        'total_stars': total_stars,
    })


def lesson_view(request, lesson_number):
    lesson = get_object_or_404(Lesson, lesson_number=lesson_number)
    user = request.user
    
    progress = None
    is_unlocked = True  # Guests can preview/try lessons
    if user.is_authenticated:
        # Check progress
        progress, _ = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'unlocked': (lesson.lesson_number == 1)}
        )
        is_unlocked = progress.unlocked

    # Find prev and next lessons
    prev_lesson = Lesson.objects.filter(lesson_number__lt=lesson.lesson_number).order_by('-lesson_number').first()
    next_lesson = Lesson.objects.filter(lesson_number__gt=lesson.lesson_number).order_by('lesson_number').first()

    return render(request, 'app/lesson.html', {
        'lesson': lesson,
        'progress': progress,
        'is_unlocked': is_unlocked,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    })


def practice_view(request):
    """Dedicated targeted practice arena for weak keys and custom repetition drills."""
    keys_param = request.GET.get('keys', '')
    keys = [k.strip().lower() for k in keys_param.split(',') if k.strip()]

    # Default to user's most missed keys if authenticated
    if not keys and request.user.is_authenticated:
        recent = TypingSession.objects.filter(user=request.user)[:15]
        agg_mistakes = {}
        for s in recent:
            if s.key_mistakes and isinstance(s.key_mistakes, dict):
                for k, v in s.key_mistakes.items():
                    agg_mistakes[k.lower()] = agg_mistakes.get(k.lower(), 0) + int(v)
        sorted_keys = sorted(agg_mistakes.items(), key=lambda x: x[1], reverse=True)
        keys = [item[0] for item in sorted_keys[:3]]

    if not keys:
        keys = ['f', 'j', 'd', 'k']

    # Generate progressive repetition drill
    part1 = " ".join([f"{k} {k} {k} {k} {k}{k}" for k in keys])
    part2 = " ".join([f"{k}f f{k} {k}j j{k}" for k in keys])
    drill_text = f"{part1} {part2}"

    return render(request, 'app/practice.html', {
        'drill_title': f"Targeted Drill: {' & '.join([k.upper() for k in keys])}",
        'target_keys': keys,
        'drill_text': drill_text,
    })


def typing_test_view(request):
    return render(request, 'app/typing_test.html')


def games_hub(request):
    return render(request, 'app/games.html')


@login_required
def achievements_view(request):
    user = request.user
    all_achievements = Achievement.objects.all().order_by('category', 'requirement_value')
    user_unlocked_ids = set(UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True))

    achievements_by_category = {}
    for ach in all_achievements:
        cat = ach.get_category_display()
        if cat not in achievements_by_category:
            achievements_by_category[cat] = []
        achievements_by_category[cat].append({
            'achievement': ach,
            'is_unlocked': ach.id in user_unlocked_ids
        })

    unlocked_count = len(user_unlocked_ids)
    total_count = all_achievements.count()
    percentage = int((unlocked_count / total_count * 100)) if total_count > 0 else 0

    return render(request, 'app/achievements.html', {
        'categories': achievements_by_category,
        'unlocked_count': unlocked_count,
        'total_count': total_count,
        'percentage': percentage,
    })


@login_required
def statistics_view(request):
    user = request.user
    sessions = TypingSession.objects.filter(user=user).order_by('created_at')
    
    # Build chart data points (last 20 sessions)
    recent_sessions = list(sessions.reverse()[:20])
    recent_sessions.reverse()
    
    labels = [s.created_at.strftime('%m/%d %H:%M') for s in recent_sessions]
    wpm_data = [round(s.wpm, 1) for s in recent_sessions]
    accuracy_data = [round(s.accuracy, 1) for s in recent_sessions]

    # Lifetime totals
    total_characters = sessions.aggregate(Sum('characters_typed'))['characters_typed__sum'] or 0
    total_time_seconds = user.profile.total_practice_time_seconds
    best_wpm = sessions.aggregate(Max('wpm'))['wpm__max'] or 0.0
    avg_wpm = sessions.aggregate(Avg('wpm'))['wpm__avg'] or 0.0
    avg_accuracy = sessions.aggregate(Avg('accuracy'))['accuracy__avg'] or 0.0

    # Aggregate weak keys
    weak_keys_dict = {}
    for s in sessions:
        if s.key_mistakes and isinstance(s.key_mistakes, dict):
            for char, count in s.key_mistakes.items():
                weak_keys_dict[char] = weak_keys_dict.get(char, 0) + int(count)

    sorted_weak_keys = sorted(weak_keys_dict.items(), key=lambda item: item[1], reverse=True)[:10]

    return render(request, 'app/statistics.html', {
        'labels_json': json.dumps(labels),
        'wpm_data_json': json.dumps(wpm_data),
        'accuracy_data_json': json.dumps(accuracy_data),
        'total_characters': total_characters,
        'total_time_minutes': total_time_seconds // 60,
        'best_wpm': round(best_wpm, 1),
        'avg_wpm': round(avg_wpm, 1),
        'avg_accuracy': round(avg_accuracy, 1),
        'weak_keys': sorted_weak_keys,
    })


@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile information has been successfully updated.")
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=user)

    # Profile statistics
    completed_lessons = LessonProgress.objects.filter(user=user, completed=True).count()
    total_stars = LessonProgress.objects.filter(user=user).aggregate(Sum('stars'))['stars__sum'] or 0
    achievements_count = UserAchievement.objects.filter(user=user).count()
    tests_count = TypingTestResult.objects.filter(user=user).count()

    return render(request, 'app/profile.html', {
        'form': form,
        'profile': profile,
        'completed_lessons': completed_lessons,
        'total_stars': total_stars,
        'achievements_count': achievements_count,
        'tests_count': tests_count,
    })


@login_required
def settings_view(request):
    user = request.user
    user_settings, _ = UserSettings.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully!")
            return redirect('settings')
    else:
        form = UserSettingsForm(instance=user_settings)

    return render(request, 'app/settings.html', {'form': form, 'settings': user_settings})


# ==========================================
# API ENDPOINTS FOR REAL-TIME CLIENT SYNC
# ==========================================

@require_POST
def api_submit_lesson(request):
    """
    Pedagogical submission handler:
    - Enforces Accuracy First (<85% requires retry, does NOT unlock next lesson).
    - Differentiates between 'COMPLETED' and 'MASTERED' (>=90% accuracy).
    - Identifies most-missed keys and suggests concrete targeted practice.
    - Reinforces skill learned and awards XP accordingly.
    """
    try:
        data = json.loads(request.body)
        lesson_id = data.get('lesson_id')
        wpm = float(data.get('wpm', 0.0))
        raw_wpm = float(data.get('raw_wpm', 0.0))
        accuracy = float(data.get('accuracy', 0.0))
        mistakes_count = int(data.get('mistakes_count', 0))
        duration_seconds = float(data.get('duration_seconds', 0.0))
        characters_typed = int(data.get('characters_typed', 0))
        key_mistakes = data.get('key_mistakes', {})

        lesson = get_object_or_404(Lesson, id=lesson_id)
        stars = lesson.calculate_stars(wpm, accuracy)
        is_mastered = lesson.is_performance_mastered(wpm, accuracy, mistakes_count)

        # Determine pedagogical status
        if accuracy < lesson.min_accuracy_threshold:
            status = 'NEEDS_PRACTICE'
            title = 'Practice Recommended'
            feedback_msg = f'Accuracy was {accuracy:.1f}%. Touch typing requires precision before speed. Aim for at least {lesson.min_accuracy_threshold:.0f}% to unlock the next lesson.'
        elif is_mastered:
            status = 'MASTERED'
            title = 'Lesson Mastered! 🏅'
            feedback_msg = f'Mastery achieved with {accuracy:.1f}% accuracy! Excellent finger habits and muscle memory.'
        else:
            status = 'COMPLETED'
            title = 'Lesson Completed'
            feedback_msg = f'Completed with {accuracy:.1f}% accuracy. Good effort! Practicing once more is recommended to reach 90%+ Mastery.'

        # Analyze most-missed keys
        sorted_missed = sorted(
            [{'key': str(k).upper(), 'count': int(v)} for k, v in key_mistakes.items() if int(v) > 0],
            key=lambda x: x['count'],
            reverse=True
        )

        # Generate targeted practice advice
        if sorted_missed:
            top_missed_str = ", ".join([f"{item['key']} ({item['count']} misses)" for item in sorted_missed[:3]])
            recommended_practice = f"Focus key recommendation: Practice {sorted_missed[0]['key']} with home row anchors for 2 minutes before moving on."
        else:
            top_missed_str = "None! Zero recurring mistakes."
            recommended_practice = "Zero persistent errors detected. Keep your rhythm smooth."

        response_data = {
            'success': True,
            'status': status,
            'title': title,
            'feedback_msg': feedback_msg,
            'recommended_practice': recommended_practice,
            'skill_learned': lesson.skill_learned,
            'most_missed_keys': sorted_missed[:5],
            'stars': stars,
            'is_mastered': is_mastered,
            'xp_earned': 0,
            'unlocked_next': False,
            'next_lesson_number': None,
            'new_achievements': []
        }

        if request.user.is_authenticated:
            user = request.user
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.update_streak()
            profile.total_practice_time_seconds += int(duration_seconds)
            
            # Log Typing Session
            TypingSession.objects.create(
                user=user,
                lesson=lesson,
                session_type='lesson',
                wpm=wpm,
                raw_wpm=raw_wpm,
                accuracy=accuracy,
                mistakes_count=mistakes_count,
                duration_seconds=duration_seconds,
                characters_typed=characters_typed,
                key_mistakes=key_mistakes
            )

            # Update Lesson Progress
            progress, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
            progress.attempts_count += 1
            if wpm > progress.best_wpm:
                progress.best_wpm = wpm
            if accuracy > progress.best_accuracy:
                progress.best_accuracy = accuracy

            is_first_time_completion = False
            # Only complete if accuracy >= threshold
            if accuracy >= lesson.min_accuracy_threshold:
                if not progress.completed:
                    is_first_time_completion = True
                    progress.completed = True
                    progress.first_completed_at = timezone.now()
                if stars > progress.stars:
                    progress.stars = stars
                if is_mastered:
                    if not progress.is_mastered:
                        progress.is_mastered = True
                    progress.mastery_count += 1
            progress.save()

            # Award XP: Base XP + Mastery Bonus
            xp_earned = 15
            if accuracy >= lesson.min_accuracy_threshold:
                xp_earned += 15 + (stars * 10)
            if is_mastered:
                xp_earned += 25
            if is_first_time_completion:
                xp_earned += 25
            
            profile.add_xp(xp_earned)
            response_data['xp_earned'] = xp_earned

            # Only unlock next lesson if threshold is met (accuracy >= 85%)
            if accuracy >= lesson.min_accuracy_threshold:
                next_lesson = Lesson.objects.filter(lesson_number__gt=lesson.lesson_number).order_by('lesson_number').first()
                if next_lesson:
                    next_progress, _ = LessonProgress.objects.get_or_create(user=user, lesson=next_lesson)
                    next_progress.unlocked = True
                    next_progress.save()
                    response_data['unlocked_next'] = True
                    response_data['next_lesson_number'] = next_lesson.lesson_number

            # Update DailyActivity
            today = timezone.localdate()
            daily_act, _ = DailyActivity.objects.get_or_create(user=user, date=today)
            daily_act.characters_typed += characters_typed
            daily_act.practice_seconds += int(duration_seconds)
            daily_act.xp_earned += xp_earned
            if is_first_time_completion:
                daily_act.lessons_completed += 1
            daily_act.save()

            # Evaluate Achievements
            new_achievements = check_user_achievements(user, wpm, accuracy, characters_typed)
            response_data['new_achievements'] = new_achievements

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def api_generate_weak_drill(request):
    """Generates a targeted drill based on weak keys with single-key reps, patterns, and words."""
    keys_param = request.GET.get('keys', '')
    keys = [k.strip().lower() for k in keys_param.split(',') if k.strip()]

    # If no keys passed, look at user's recent sessions
    if not keys and request.user.is_authenticated:
        recent = TypingSession.objects.filter(user=request.user)[:10]
        agg_mistakes = {}
        for s in recent:
            if s.key_mistakes and isinstance(s.key_mistakes, dict):
                for k, v in s.key_mistakes.items():
                    agg_mistakes[k.lower()] = agg_mistakes.get(k.lower(), 0) + int(v)
        sorted_keys = sorted(agg_mistakes.items(), key=lambda x: x[1], reverse=True)
        keys = [item[0] for item in sorted_keys[:3]]

    if not keys:
        keys = ['f', 'j']

    # Build progressive drill:
    # 1. Single-key reps
    part1 = " ".join([f"{k} {k} {k} {k} {k}{k}" for k in keys])
    # 2. Alternating pairs with home anchors f and j
    part2 = " ".join([f"{k}f f{k} {k}j j{k}" for k in keys])
    # 3. Simple combinations
    combos = []
    for k in keys:
        combos.extend([f"{k}a", f"a{k}", f"{k}s", f"s{k}", f"{k}d", f"d{k}"])
    part3 = " ".join(combos[:8])

    drill_text = f"{part1} {part2} {part3}"

    return JsonResponse({
        'success': True,
        'keys': keys,
        'drill_text': drill_text,
        'title': f"Targeted Drill: {' & '.join([k.upper() for k in keys])}"
    })



@require_POST
def api_submit_test(request):
    """Saves typing test results and awards XP."""
    try:
        data = json.loads(request.body)
        duration_mode = int(data.get('duration_mode', 60))
        wpm = float(data.get('wpm', 0.0))
        raw_wpm = float(data.get('raw_wpm', 0.0))
        accuracy = float(data.get('accuracy', 0.0))
        correct_chars = int(data.get('correct_chars', 0))
        incorrect_chars = int(data.get('incorrect_chars', 0))
        total_chars = int(data.get('total_chars', 0))

        response_data = {
            'success': True,
            'xp_earned': 0,
            'new_achievements': []
        }

        if request.user.is_authenticated:
            user = request.user
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.update_streak()
            profile.total_practice_time_seconds += duration_mode

            TypingTestResult.objects.create(
                user=user,
                duration_mode=duration_mode,
                wpm=wpm,
                raw_wpm=raw_wpm,
                accuracy=accuracy,
                correct_chars=correct_chars,
                incorrect_chars=incorrect_chars,
                total_chars=total_chars
            )

            TypingSession.objects.create(
                user=user,
                session_type='test',
                wpm=wpm,
                raw_wpm=raw_wpm,
                accuracy=accuracy,
                mistakes_count=incorrect_chars,
                duration_seconds=duration_mode,
                characters_typed=total_chars
            )

            # Test XP: scales with WPM and accuracy
            xp_earned = int(wpm * 0.75 + (accuracy / 2.0))
            profile.add_xp(xp_earned)
            response_data['xp_earned'] = xp_earned

            # Check achievements
            new_achievements = check_user_achievements(user, wpm, accuracy, total_chars)
            response_data['new_achievements'] = new_achievements

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def check_user_achievements(user, current_wpm, current_accuracy, current_chars):
    """Evaluates milestone conditions and unlocks new achievements."""
    unlocked_achievements = []
    already_unlocked = set(UserAchievement.objects.filter(user=user).values_list('achievement__code', flat=True))

    profile = user.profile
    completed_lessons_count = LessonProgress.objects.filter(user=user, completed=True).count()
    all_sessions = TypingSession.objects.filter(user=user)
    total_chars_typed = all_sessions.aggregate(Sum('characters_typed'))['characters_typed__sum'] or 0

    to_check = [
        ('first_lesson', completed_lessons_count >= 1),
        ('home_row_hero', completed_lessons_count >= 10),
        ('ten_lessons', completed_lessons_count >= 10),
        ('twenty_five_lessons', completed_lessons_count >= 25),
        ('course_graduate', completed_lessons_count >= 54),
        ('speed_30', current_wpm >= 30),
        ('speed_50', current_wpm >= 50),
        ('speed_75', current_wpm >= 75),
        ('speed_100', current_wpm >= 100),
        ('accuracy_90', current_accuracy >= 90),
        ('accuracy_95', current_accuracy >= 95),
        ('accuracy_100', current_accuracy >= 100),
        ('streak_3', profile.current_streak >= 3),
        ('streak_7', profile.current_streak >= 7),
        ('streak_30', profile.current_streak >= 30),
        ('chars_1000', total_chars_typed >= 1000),
        ('chars_10000', total_chars_typed >= 10000),
    ]

    for code, condition in to_check:
        if condition and code not in already_unlocked:
            try:
                ach = Achievement.objects.get(code=code)
                UserAchievement.objects.create(user=user, achievement=ach)
                profile.add_xp(ach.xp_reward)
                unlocked_achievements.append({
                    'code': ach.code,
                    'title': ach.title,
                    'description': ach.description,
                    'xp': ach.xp_reward,
                    'icon': ach.icon
                })
            except Achievement.DoesNotExist:
                pass

    return unlocked_achievements


def health_check(request):
    """
    Health check endpoint for Render health monitoring and status probes.
    Verifies application execution and database connectivity.
    """
    from django.db import connection
    from django.conf import settings

    db_status = "connected"
    status_code = 200
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
    except Exception as e:
        db_status = f"unavailable: {str(e)}"
        status_code = 503

    return JsonResponse({
        "status": "healthy" if status_code == 200 else "unhealthy",
        "database": db_status,
        "environment": "development" if settings.DEBUG else "production",
    }, status=status_code)

