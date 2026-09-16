from django.urls import path
from . import views

urlpatterns = [
    # Marketing / Public Pages
    path('', views.landing, name='landing'),
    path('about/', views.about, name='about'),
    path('help/', views.help_faq, name='help'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password-done/', views.reset_password_done_view, name='reset_password_done'),

    # Application Pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('lessons/', views.course_map, name='course_map'),
    path('lesson/<int:lesson_number>/', views.lesson_view, name='lesson_view'),
    path('test/', views.typing_test_view, name='typing_test'),
    path('games/', views.games_hub, name='games'),
    path('achievements/', views.achievements_view, name='achievements'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('practice/', views.practice_view, name='practice'),

    # Real-Time API Endpoints
    path('api/lesson/submit/', views.api_submit_lesson, name='api_submit_lesson'),
    path('api/test/submit/', views.api_submit_test, name='api_submit_test'),
    path('api/drill/generate/', views.api_generate_weak_drill, name='api_generate_weak_drill'),
]

