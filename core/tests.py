from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import (
    UserProfile, UserSettings, Course, Lesson, LessonProgress,
    TypingSession, TypingTestResult, Achievement, UserAchievement
)
import json

class TypeRiseModelTests(TestCase):
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


class TypeRiseViewAndAPITests(TestCase):
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
        for route in ['landing', 'about', 'developer', 'help', 'login', 'signup', 'typing_test', 'games']:
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200, f"Route {route} failed to return 200")

    def test_developer_profile_content(self):
        # Verify /developer page content
        response = self.client.get(reverse('developer'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kaushal Singh Ahirwar')
        self.assertContains(response, 'Full-stack Developer')
        self.assertContains(response, 'TypeRise — Creator &amp; Developer')
        self.assertContains(response, 'developer.png')
        self.assertContains(response, 'https://www.linkedin.com/in/kaushal-singh-ahirwar')
        self.assertContains(response, 'https://kaushal-port.netlify.app/')

        # Verify /about page also contains Meet the Developer section
        about_response = self.client.get(reverse('about'))
        self.assertEqual(about_response.status_code, 200)
        self.assertContains(about_response, 'Meet the Developer')
        self.assertContains(about_response, 'Kaushal Singh Ahirwar')
        self.assertContains(about_response, 'developer.png')


    def test_signup_creates_account_and_logs_in(self):
        from core.models import EmailOTP
        # Step 1: Initial signup triggers OTP dispatch
        response = self.client.post(reverse('signup'), {
            'name': 'Alice Wonder',
            'email': 'alice@example.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_otp'))

        # Verify OTP was created in database
        otp = EmailOTP.objects.filter(email='alice@example.com', purpose=EmailOTP.PURPOSE_SIGNUP).first()
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.otp_code), 6)

        # Step 2: Submit valid OTP to complete registration
        verify_response = self.client.post(reverse('verify_otp'), {
            'otp_code': otp.otp_code
        })
        self.assertEqual(verify_response.status_code, 302)
        self.assertRedirects(verify_response, reverse('dashboard'))

        # User is now created and authenticated
        self.assertTrue(User.objects.filter(email='alice@example.com').exists())
        user = User.objects.get(email='alice@example.com')
        self.assertEqual(user.first_name, 'Alice')
        self.assertEqual(user.last_name, 'Wonder')

    def test_forgot_password_and_reset_with_otp(self):
        from core.models import EmailOTP
        # Request password reset OTP
        res = self.client.post(reverse('forgot_password'), {
            'email': self.user.email
        })
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('reset_password_otp'))

        otp = EmailOTP.objects.filter(email=self.user.email, purpose=EmailOTP.PURPOSE_FORGOT_PASSWORD).first()
        self.assertIsNotNone(otp)

        # Reset password with OTP
        reset_res = self.client.post(reverse('reset_password_otp'), {
            'otp_code': otp.otp_code,
            'new_password': 'BrandNewPassword2026!',
            'confirm_password': 'BrandNewPassword2026!'
        })
        self.assertEqual(reset_res.status_code, 302)
        self.assertRedirects(reset_res, reverse('login'))

        # Check new password works
        login_res = self.client.login(username=self.user.username, password='BrandNewPassword2026!')
        self.assertTrue(login_res)


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

    def test_low_accuracy_blocks_unlocking_and_flags_needs_practice(self):
        self.client.login(username='speedster', password='StrongPassword123')

        # Submit lesson with 80% accuracy (< 85% threshold)
        payload = {
            'lesson_id': self.lesson1.id,
            'wpm': 25.0,
            'raw_wpm': 28.0,
            'accuracy': 80.0,
            'mistakes_count': 6,
            'duration_seconds': 14.0,
            'characters_typed': 30,
            'key_mistakes': {'f': 4, 'j': 2}
        }
        response = self.client.post(
            reverse('api_submit_lesson'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'NEEDS_PRACTICE')
        self.assertFalse(data['unlocked_next'])
        self.assertEqual(data['stars'], 0)
        self.assertIn('Focus key recommendation', data['recommended_practice'])

        # Confirm next lesson remains locked
        progress2 = LessonProgress.objects.filter(user=self.user, lesson=self.lesson2).first()
        self.assertTrue(progress2 is None or not progress2.unlocked)

    def test_high_accuracy_awards_mastery(self):
        self.client.login(username='speedster', password='StrongPassword123')

        # Submit lesson with 95% accuracy and good WPM
        payload = {
            'lesson_id': self.lesson1.id,
            'wpm': 25.0,
            'raw_wpm': 26.0,
            'accuracy': 95.0,
            'mistakes_count': 1,
            'duration_seconds': 10.0,
            'characters_typed': 30,
            'key_mistakes': {'j': 1}
        }
        response = self.client.post(
            reverse('api_submit_lesson'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'MASTERED')
        self.assertTrue(data['is_mastered'])
        self.assertTrue(data['unlocked_next'])

        # Verify LessonProgress has is_mastered = True
        progress1 = LessonProgress.objects.get(user=self.user, lesson=self.lesson1)
        self.assertTrue(progress1.is_mastered)
        self.assertGreaterEqual(progress1.mastery_count, 1)

    def test_api_generate_weak_drill(self):
        response = self.client.get(reverse('api_generate_weak_drill') + '?keys=f,j')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['keys'], ['f', 'j'])
        self.assertIn('f', data['drill_text'])
        self.assertIn('j', data['drill_text'])

    def test_email_otp_generation_and_verification(self):
        from core.email_service import create_and_send_otp, verify_otp_code, can_request_otp
        from core.models import EmailOTP
        from django.utils import timezone
        from datetime import timedelta

        # Successful OTP creation
        ok, msg = create_and_send_otp('newtypist@example.com', EmailOTP.PURPOSE_SIGNUP, user_name='Newbie')
        self.assertTrue(ok)
        otp = EmailOTP.objects.filter(email='newtypist@example.com', purpose=EmailOTP.PURPOSE_SIGNUP, is_used=False).first()
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.otp_code), 6)
        self.assertEqual(otp.failed_attempts, 0)

        # 60s cooldown prevents rapid re-requesting
        can_req, wait_secs = can_request_otp('newtypist@example.com', EmailOTP.PURPOSE_SIGNUP)
        self.assertFalse(can_req)
        self.assertGreater(wait_secs, 0)

        # Invalid code increments failed_attempts
        valid, err = verify_otp_code('newtypist@example.com', '000000', EmailOTP.PURPOSE_SIGNUP)
        self.assertFalse(valid)
        otp.refresh_from_db()
        self.assertEqual(otp.failed_attempts, 1)

        # Test lockout after 5 failed attempts
        otp.failed_attempts = 4
        otp.save()
        valid, lock_err = verify_otp_code('newtypist@example.com', '000000', EmailOTP.PURPOSE_SIGNUP)
        self.assertFalse(valid)
        self.assertIn("invalidated", lock_err.lower())
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)

        # Expired code check
        expired_otp = EmailOTP.objects.create(
            email='expired@example.com',
            otp_code='123456',
            purpose=EmailOTP.PURPOSE_SIGNUP,
            expires_at=timezone.now() - timedelta(minutes=1),
            is_used=False
        )
        valid, exp_err = verify_otp_code('expired@example.com', '123456', EmailOTP.PURPOSE_SIGNUP)
        self.assertFalse(valid)
        self.assertIn("expired", exp_err.lower())

    def test_signup_pending_state_and_activation(self):
        from core.models import EmailOTP
        from unittest.mock import patch

        signup_data = {
            'name': 'Rahul Sharma',
            'email': 'rahul@example.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
        }

        with patch('django.core.mail.EmailMultiAlternatives.send', return_value=1):
            response = self.client.post(reverse('signup'), data=signup_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('verify_otp'))

        # User must exist in pending/unverified state (is_active=False)
        user = User.objects.filter(email='rahul@example.com').first()
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)

        # Fetch dispatched OTP
        otp_record = EmailOTP.objects.filter(email='rahul@example.com', purpose=EmailOTP.PURPOSE_SIGNUP, is_used=False).first()
        self.assertIsNotNone(otp_record)

        # Attempt verification with wrong OTP
        verify_fail = self.client.post(reverse('verify_otp'), {'otp_code': '999999'})
        user.refresh_from_db()
        self.assertFalse(user.is_active)

        # Verify with correct OTP
        verify_success = self.client.post(reverse('verify_otp'), {'otp_code': otp_record.otp_code})
        self.assertEqual(verify_success.status_code, 302)
        self.assertRedirects(verify_success, reverse('dashboard'))

        # User is now activated!
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        # Dashboard accessible because user was logged in
        dash_resp = self.client.get(reverse('dashboard'))
        self.assertEqual(dash_resp.status_code, 200)

    def test_signup_email_send_failure_shows_friendly_message(self):
        from unittest.mock import patch

        signup_data = {
            'name': 'Failure Test',
            'email': 'failtest@example.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
        }

        # Mock unexpected mailer error
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=ValueError("Unexpected mailer error")):
            response = self.client.post(reverse('signup'), data=signup_data, follow=True)
            self.assertEqual(response.status_code, 200)
            messages_list = list(response.context['messages'])
            self.assertTrue(any("Unable to send the email right now. Please try again later." in str(m) for m in messages_list))

    def test_render_firewall_blocks_smtp_surfaces_otp(self):
        from unittest.mock import patch

        signup_data = {
            'name': 'Render Test',
            'email': 'rendertest@example.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
        }

        # Simulate Render free-tier firewall blocking outbound SMTP port 587
        with patch('django.core.mail.EmailMultiAlternatives.send', side_effect=OSError(101, 'Network is unreachable')):
            response = self.client.post(reverse('signup'), data=signup_data, follow=True)
            self.assertEqual(response.status_code, 200)
            messages_list = list(response.context['messages'])
            self.assertTrue(any("Render Free Tier blocked SMTP port 587" in str(m) for m in messages_list))
            self.assertTrue(any("your verification code is:" in str(m) for m in messages_list))

    def test_forgot_password_and_reset_flow(self):
        from core.models import EmailOTP
        from unittest.mock import patch

        test_user = User.objects.create_user(
            username='forgotten_hero',
            email='hero@example.com',
            password='OldPassword123!',
            is_active=True
        )

        # Request reset OTP
        with patch('django.core.mail.EmailMultiAlternatives.send', return_value=1):
            response = self.client.post(reverse('forgot_password'), {'email': 'hero@example.com'})
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('reset_password_otp'))

        otp_record = EmailOTP.objects.filter(email='hero@example.com', purpose=EmailOTP.PURPOSE_FORGOT_PASSWORD, is_used=False).first()
        self.assertIsNotNone(otp_record)

        # Submit OTP + new password
        reset_resp = self.client.post(reverse('reset_password_otp'), {
            'otp_code': otp_record.otp_code,
            'new_password': 'BrandNewPassword123!',
            'confirm_password': 'BrandNewPassword123!',
        })
        self.assertEqual(reset_resp.status_code, 302)
        self.assertRedirects(reset_resp, reverse('login'))

        # Old password no longer works via login view
        bad_login = self.client.post(reverse('login'), {'username': 'hero@example.com', 'password': 'OldPassword123!'})
        self.assertFalse(bad_login.context['user'].is_authenticated if 'user' in (bad_login.context or {}) else False)

        # New password works via login view (supports login via email)
        good_login = self.client.post(reverse('login'), {'username': 'hero@example.com', 'password': 'BrandNewPassword123!'})
        self.assertEqual(good_login.status_code, 302)
        self.assertRedirects(good_login, reverse('dashboard'))

        # Also works via direct username login
        self.assertTrue(self.client.login(username='forgotten_hero', password='BrandNewPassword123!'))

