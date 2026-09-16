from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import (
    UserProfile, UserSettings, Course, Lesson, LessonProgress,
    TypingSession, TypingTestResult, Achievement, UserAchievement
)
import json

class TypeForgeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='typist_pro',
            email='typist@example.com',
            password='Password123!'
        )
        self.course = Course.objects.create(
            title='Touch Typing Mastery',
            slug='touch-typing-mastery',
            description='Complete touch typing curriculum',
            order=1
        )
        self.lesson1 = Lesson.objects.create(
            course=self.course,
            level_number=1,
            level_title='Level 1: Getting Started',
            lesson_number=1,
            title='Introduction to the Home Row',
            slug='intro-home-row',
            learning_objective='Learn F and J bumps',
            instruction='Rest on F and J',
            target_text='f j f j',
            keys_introduced='f, j',
            min_wpm_3stars=10,
            min_wpm_4stars=18,
            min_wpm_5stars=25,
            min_accuracy_threshold=85.0
        )
        self.lesson2 = Lesson.objects.create(
            course=self.course,
            level_number=1,
            level_title='Level 1: Getting Started',
            lesson_number=2,
            title='The F and J Keys',
            slug='f-and-j-keys',
            learning_objective='Develop muscle memory',
            instruction='Alternate F and J',
            target_text='fj jf fj jf',
            keys_introduced='f, j',
            min_wpm_3stars=12,
            min_wpm_4stars=20,
            min_wpm_5stars=28,
            min_accuracy_threshold=85.0
        )
        self.achievement = Achievement.objects.create(
            code='first_lesson',
            title='First Step',
            description='Complete your first lesson',
            category='lessons',
            icon='play',
            requirement_value=1.0,
            xp_reward=50
        )

    def test_user_profile_and_settings_auto_created(self):
        self.assertIsNotNone(self.user.profile)
        self.assertIsNotNone(self.user.settings)
        self.assertEqual(self.user.profile.level, 1)
        self.assertEqual(self.user.profile.xp, 0)
        self.assertTrue(self.user.settings.sound_enabled)

    def test_star_calculation_logic(self):
        # Failing accuracy
        self.assertEqual(self.lesson1.calculate_stars(wpm=40, accuracy=80.0), 0)
        # 1 star (barely passed)
        self.assertEqual(self.lesson1.calculate_stars(wpm=8, accuracy=86.0), 1)
        # 2 stars
        self.assertEqual(self.lesson1.calculate_stars(wpm=8, accuracy=89.0), 2)
        # 3 stars
        self.assertEqual(self.lesson1.calculate_stars(wpm=12, accuracy=92.0), 3)
        # 4 stars
        self.assertEqual(self.lesson1.calculate_stars(wpm=20, accuracy=96.0), 4)
        # 5 stars
        self.assertEqual(self.lesson1.calculate_stars(wpm=30, accuracy=99.0), 5)

    def test_streak_and_xp_update(self):
        profile = self.user.profile
        profile.update_streak()
        self.assertEqual(profile.current_streak, 1)
        profile.add_xp(450)
        # 1 + (450 // 200) = Level 3
        self.assertEqual(profile.level, 3)


class TypeForgeViewAndAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='speedster',
            email='speedster@example.com',
            password='StrongPassword123'
        )
        self.course = Course.objects.create(
            title='Touch Typing Mastery',
            slug='touch-typing-mastery',
            description='Test course'
        )
        self.lesson1 = Lesson.objects.create(
            course=self.course,
            level_number=1,
            level_title='Level 1',
            lesson_number=1,
            title='Lesson 1',
            slug='lesson-1',
            learning_objective='Learn F J',
            instruction='Type F J',
            target_text='f j f j',
            min_wpm_3stars=10,
            min_wpm_4stars=20,
            min_wpm_5stars=30,
            min_accuracy_threshold=85.0
        )
        self.lesson2 = Lesson.objects.create(
            course=self.course,
            level_number=1,
            level_title='Level 1',
            lesson_number=2,
            title='Lesson 2',
            slug='lesson-2',
            learning_objective='Learn D K',
            instruction='Type D K',
            target_text='d k d k',
            min_wpm_3stars=10,
            min_wpm_4stars=20,
            min_wpm_5stars=30,
            min_accuracy_threshold=85.0
        )
        self.achievement = Achievement.objects.create(
            code='first_lesson',
            title='First Step',
            description='Complete your first lesson',
            category='lessons',
            icon='play',
            requirement_value=1.0,
            xp_reward=50
        )

    def test_public_pages_render(self):
        for route in ['landing', 'about', 'help', 'login', 'signup', 'typing_test', 'games']:
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200, f"Route {route} failed to return 200")

    def test_signup_creates_account_and_logs_in(self):
        response = self.client.post(reverse('signup'), {
            'name': 'Alice Wonder',
            'email': 'alice@example.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='alice@example.com').exists())

    def test_login_and_dashboard_access(self):
        login_success = self.client.login(username='speedster', password='StrongPassword123')
        self.assertTrue(login_success)
        dashboard_res = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_res.status_code, 200)
        self.assertContains(dashboard_res, 'speedster')

    def test_api_submit_lesson_unlocks_next_lesson(self):
        self.client.login(username='speedster', password='StrongPassword123')

        payload = {
            'lesson_id': self.lesson1.id,
            'wpm': 32.5,
            'raw_wpm': 33.0,
            'accuracy': 98.0,
            'mistakes_count': 1,
            'duration_seconds': 12.5,
            'characters_typed': 30,
            'key_mistakes': {'f': 1}
        }
        response = self.client.post(
            reverse('api_submit_lesson'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['stars'], 5)
        self.assertTrue(data['unlocked_next'])
        self.assertEqual(data['next_lesson_number'], 2)

        # Verify database update
        progress2 = LessonProgress.objects.get(user=self.user, lesson=self.lesson2)
        self.assertTrue(progress2.unlocked)

        # Verify achievement unlocked
        self.assertTrue(UserAchievement.objects.filter(user=self.user, achievement=self.achievement).exists())

    def test_api_submit_typing_test(self):
        self.client.login(username='speedster', password='StrongPassword123')

        payload = {
            'duration_mode': 60,
            'wpm': 55.0,
            'raw_wpm': 58.0,
            'accuracy': 96.0,
            'correct_chars': 275,
            'incorrect_chars': 10,
            'total_chars': 285
        }
        response = self.client.post(
            reverse('api_submit_test'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertGreater(data['xp_earned'], 0)
        self.assertTrue(TypingTestResult.objects.filter(user=self.user).exists())
