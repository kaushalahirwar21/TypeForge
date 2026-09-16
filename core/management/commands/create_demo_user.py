from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, Lesson, LessonProgress, TypingSession, TypingTestResult, Achievement, UserAchievement
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Creates a pre-configured demo user with realistic typing activity for immediate exploration'

    def handle(self, *args, **options):
        username = 'demo'
        email = 'demo@typeforge.local'
        password = 'Password123!'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Alex',
                'last_name': 'Morgan'
            }
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.current_streak = 5
        profile.best_streak = 12
        profile.last_active_date = timezone.localdate()
        profile.total_practice_time_seconds = 3600 * 3 + 1200 # ~3.3 hours
        profile.xp = 1850
        profile.level = 10
        profile.save()

        # Unlock and complete first 12 lessons
        lessons = Lesson.objects.order_by('lesson_number')[:15]
        for idx, lesson in enumerate(lessons):
            is_completed = idx < 12
            progress, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
            progress.unlocked = True
            progress.completed = is_completed
            progress.stars = 5 if idx < 8 else (4 if is_completed else 0)
            progress.best_wpm = 45.0 + (idx * 2.5) if is_completed else 0.0
            progress.best_accuracy = 97.5 if is_completed else 0.0
            progress.attempts_count = 2 if is_completed else 0
            progress.save()

            if is_completed:
                # Create session history
                TypingSession.objects.get_or_create(
                    user=user,
                    lesson=lesson,
                    session_type='lesson',
                    defaults={
                        'wpm': progress.best_wpm,
                        'raw_wpm': progress.best_wpm + 3.0,
                        'accuracy': progress.best_accuracy,
                        'mistakes_count': 2,
                        'duration_seconds': 45.0,
                        'characters_typed': len(lesson.target_text),
                        'key_mistakes': {'q': 3, 'p': 2, 'z': 1}
                    }
                )

        # Create sample typing tests
        TypingTestResult.objects.get_or_create(
            user=user,
            duration_mode=60,
            defaults={
                'wpm': 68.5,
                'raw_wpm': 71.0,
                'accuracy': 98.2,
                'correct_chars': 342,
                'incorrect_chars': 6,
                'total_chars': 348
            }
        )

        # Award several achievements
        sample_codes = ['first_lesson', 'home_row_hero', 'ten_lessons', 'speed_30', 'speed_50', 'accuracy_95', 'streak_3']
        for code in sample_codes:
            try:
                ach = Achievement.objects.get(code=code)
                UserAchievement.objects.get_or_create(user=user, achievement=ach)
            except Achievement.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS(f"Demo user '{username}' configured successfully! Password: '{password}'"))
