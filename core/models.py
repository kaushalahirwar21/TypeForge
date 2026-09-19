from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    current_streak = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    total_practice_time_seconds = models.PositiveIntegerField(default=0)
    avatar_color = models.CharField(max_length=20, default='#3b82f6')

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} (Lvl {self.level}, {self.xp} XP)"

    def update_streak(self):
        today = timezone.localdate()
        if not self.last_active_date:
            self.current_streak = 1
        elif self.last_active_date == today:
            pass  # Already active today
        elif self.last_active_date == today - datetime.timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1

        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak
        self.last_active_date = today

    def add_xp(self, amount):
        self.xp += amount
        # Level formula: Level = 1 + int(XP / 200)
        new_level = 1 + (self.xp // 200)
        if new_level > self.level:
            self.level = new_level
        self.save()

    @property
    def xp_current_level_progress(self):
        level_start_xp = (self.level - 1) * 200
        current_in_level = self.xp - level_start_xp
        return min(100, int((current_in_level / 200.0) * 100))


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    sound_enabled = models.BooleanField(default=True)
    keyboard_visible = models.BooleanField(default=True)
    hand_guide_visible = models.BooleanField(default=True)
    font_size = models.CharField(max_length=10, choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large')
    ], default='medium')
    theme = models.CharField(max_length=20, choices=[
        ('light', 'Light Classic'),
        ('slate', 'Modern Slate'),
        ('dark', 'Dark Night')
    ], default='slate')
    instant_feedback = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'User Settings'
        verbose_name_plural = 'User Settings'

    def __str__(self):
        return f"Settings for {self.user.username}"


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserSettings.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        if hasattr(instance, 'settings'):
            instance.settings.save()


class Course(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='keyboard')
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    STAGES = [
        ('foundation', 'Foundation & Posture'),
        ('home_row', 'Home Row'),
        ('top_row', 'Top Row'),
        ('bottom_row', 'Bottom Row'),
        ('full_alphabet', 'Full Alphabet'),
        ('capital_letters', 'Capital Letters & Shift'),
        ('numbers', 'Numbers Row'),
        ('symbols', 'Symbols & Punctuation'),
        ('common_words', 'High Frequency Words'),
        ('sentences', 'Sentences & Flow'),
        ('paragraphs', 'Paragraphs & Literature'),
        ('speed_training', 'Speed Training'),
        ('accuracy_training', 'Accuracy Training'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    stage = models.CharField(max_length=30, choices=STAGES, default='home_row', db_index=True)
    level_number = models.PositiveIntegerField(default=1, db_index=True)
    level_title = models.CharField(max_length=100, default='Level 1')
    lesson_number = models.PositiveIntegerField(db_index=True)
    title = models.CharField(max_length=150)
    slug = models.SlugField()
    learning_objective = models.CharField(max_length=255)
    instruction = models.TextField(help_text="Instructions shown to the user before or during typing")
    target_text = models.TextField(help_text="The exact text the user must type")
    keys_introduced = models.CharField(max_length=100, blank=True, help_text="e.g. 'f, j'")

    # Pre-typing Teacher Module Details
    key_name = models.CharField(max_length=100, default='Home Row Keys')
    target_finger = models.CharField(max_length=100, default='Index Fingers')
    finger_hand = models.CharField(max_length=100, default='Left & Right Hands')
    finger_why = models.TextField(default="Anchor your hands on the home row using the small physical ridges on F and J.")
    skill_learned = models.CharField(max_length=255, default="Practiced correct finger placement and muscle memory.")
    spaced_repetition_keys = models.CharField(max_length=150, blank=True, help_text="Previously learned keys reinforced")

    # Thresholds for stars & mastery
    min_wpm_3stars = models.PositiveIntegerField(default=15)
    min_wpm_4stars = models.PositiveIntegerField(default=25)
    min_wpm_5stars = models.PositiveIntegerField(default=35)
    min_accuracy_threshold = models.FloatField(default=85.0, help_text="Minimum accuracy % to complete (unlock next)")
    min_mastery_accuracy = models.FloatField(default=90.0, help_text="Minimum accuracy % for mastery badge")

    class Meta:
        ordering = ['level_number', 'lesson_number']
        unique_together = ('course', 'lesson_number')

    def __str__(self):
        return f"L{self.level_number}.{self.lesson_number}: {self.title}"

    def calculate_stars(self, wpm, accuracy):
        if accuracy < self.min_accuracy_threshold:
            return 0  # Needs Practice (below 85%)
        if accuracy >= 98 and wpm >= self.min_wpm_5stars:
            return 5
        elif accuracy >= 95 and wpm >= self.min_wpm_4stars:
            return 4
        elif accuracy >= 90 and wpm >= self.min_wpm_3stars:
            return 3
        elif accuracy >= 88:
            return 2
        else:
            return 1

    def is_performance_mastered(self, wpm, accuracy, mistakes_count):
        # Mastery requires >= 90% accuracy and controlled mistakes
        return accuracy >= self.min_mastery_accuracy and mistakes_count <= 4


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    completed = models.BooleanField(default=False)
    is_mastered = models.BooleanField(default=False)
    mastery_count = models.PositiveIntegerField(default=0)
    unlocked = models.BooleanField(default=False)
    stars = models.PositiveSmallIntegerField(default=0)  # 0 to 5
    best_wpm = models.FloatField(default=0.0)
    best_accuracy = models.FloatField(default=0.0)
    attempts_count = models.PositiveIntegerField(default=0)
    first_completed_at = models.DateTimeField(null=True, blank=True)
    last_attempted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')
        indexes = [
            models.Index(fields=['user', 'completed']),
            models.Index(fields=['user', 'is_mastered']),
            models.Index(fields=['user', 'lesson']),
        ]

    def __str__(self):
        status = "Mastered" if self.is_mastered else ("Completed" if self.completed else "In Progress")
        return f"{self.user.username} - {self.lesson.title}: {self.stars}★ ({status})"


class TypingSession(models.Model):
    SESSION_TYPES = [
        ('lesson', 'Lesson'),
        ('test', 'Typing Test'),
        ('game', 'Game'),
        ('practice', 'Free Practice'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='typing_sessions', null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='lesson')
    wpm = models.FloatField(default=0.0)
    raw_wpm = models.FloatField(default=0.0)
    accuracy = models.FloatField(default=0.0)
    mistakes_count = models.PositiveIntegerField(default=0)
    duration_seconds = models.FloatField(default=0.0)
    characters_typed = models.PositiveIntegerField(default=0)
    key_mistakes = models.JSONField(default=dict, blank=True, help_text="Dict of character mistakes count, e.g. {'f': 3, 'j': 1}")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username if self.user else 'Guest'} - {self.session_type} - {self.wpm:.1f} WPM ({self.accuracy:.1f}%)"


class TypingTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='typing_test_results', null=True, blank=True)
    duration_mode = models.PositiveIntegerField(choices=[(30, '30 Seconds'), (60, '60 Seconds'), (120, '120 Seconds')], default=60)
    wpm = models.FloatField(default=0.0)
    raw_wpm = models.FloatField(default=0.0)
    accuracy = models.FloatField(default=0.0)
    correct_chars = models.PositiveIntegerField(default=0)
    incorrect_chars = models.PositiveIntegerField(default=0)
    total_chars = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username if self.user else 'Guest'} - {self.duration_mode}s Test: {self.wpm:.1f} WPM"


class Achievement(models.Model):
    CATEGORIES = [
        ('lessons', 'Lessons & Learning'),
        ('speed', 'Typing Speed'),
        ('accuracy', 'Accuracy'),
        ('streak', 'Streaks & Consistency'),
        ('volume', 'Practice Volume'),
    ]

    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORIES, default='lessons')
    icon = models.CharField(max_length=50, default='trophy')
    requirement_value = models.FloatField(default=1.0)
    xp_reward = models.PositiveIntegerField(default=50)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='awarded_to')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.user.username} unlocked {self.achievement.title}"


class DailyActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField(default=timezone.localdate, db_index=True)
    characters_typed = models.PositiveIntegerField(default=0)
    practice_seconds = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.characters_typed} chars"


class EmailOTP(models.Model):
    PURPOSE_SIGNUP = 'signup'
    PURPOSE_FORGOT_PASSWORD = 'forgot_password'
    PURPOSE_CHOICES = [
        (PURPOSE_SIGNUP, 'Signup Verification'),
        (PURPOSE_FORGOT_PASSWORD, 'Password Reset'),
    ]

    email = models.EmailField(db_index=True)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    failed_attempts = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Email OTP'
        verbose_name_plural = 'Email OTPs'
        ordering = ['-created_at']

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at and self.failed_attempts < 5

    def __str__(self):
        return f"{self.email} ({self.purpose}) - Used: {self.is_used}"

