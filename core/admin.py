from django.contrib import admin
from .models import (
    UserProfile, UserSettings, Course, Lesson,
    LessonProgress, TypingSession, TypingTestResult,
    Achievement, UserAchievement, DailyActivity
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'xp', 'current_streak', 'best_streak', 'total_practice_time_seconds', 'last_active_date')
    search_fields = ('user__username', 'user__email')
    list_filter = ('level',)

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'sound_enabled', 'keyboard_visible', 'hand_guide_visible', 'font_size', 'theme')
    search_fields = ('user__username',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'level_number', 'lesson_number', 'title', 'course', 'keys_introduced', 'min_wpm_3stars')
    list_filter = ('level_number', 'course')
    search_fields = ('title', 'instruction', 'target_text')
    ordering = ('level_number', 'lesson_number')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'unlocked', 'stars', 'best_wpm', 'best_accuracy', 'attempts_count')
    list_filter = ('completed', 'unlocked', 'stars')
    search_fields = ('user__username', 'lesson__title')

@admin.register(TypingSession)
class TypingSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_type', 'lesson', 'wpm', 'accuracy', 'mistakes_count', 'duration_seconds', 'created_at')
    list_filter = ('session_type', 'created_at')
    search_fields = ('user__username',)

@admin.register(TypingTestResult)
class TypingTestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'duration_mode', 'wpm', 'accuracy', 'correct_chars', 'incorrect_chars', 'created_at')
    list_filter = ('duration_mode', 'created_at')
    search_fields = ('user__username',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'category', 'requirement_value', 'xp_reward')
    list_filter = ('category',)
    search_fields = ('title', 'code')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')
    list_filter = ('unlocked_at',)
    search_fields = ('user__username', 'achievement__title')

@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'characters_typed', 'practice_seconds', 'lessons_completed', 'xp_earned')
    list_filter = ('date',)
    search_fields = ('user__username',)
