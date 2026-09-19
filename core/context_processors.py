from django.conf import settings
from .models import UserProfile, UserSettings

def site_settings(request):
    """Context processor providing universal TypeForge context across all templates."""
    context = {
        'SITE_NAME': 'TypeForge',
        'SITE_TAGLINE': 'Master Touch Typing with Precision & Speed',
        'DEVELOPER_NAME': getattr(settings, 'DEVELOPER_NAME', 'Kaushal Singh Ahirwar'),
        'DEVELOPER_ROLE': getattr(settings, 'DEVELOPER_ROLE', 'Full-stack Developer'),
        'DEVELOPER_TYPEFORGE_ROLE': getattr(settings, 'DEVELOPER_TYPEFORGE_ROLE', 'TypeForge — Creator & Developer'),
        'DEVELOPER_LINKEDIN_URL': getattr(settings, 'DEVELOPER_LINKEDIN_URL', 'https://www.linkedin.com/in/kaushal-singh-ahirwar'),
        'DEVELOPER_PORTFOLIO_URL': getattr(settings, 'DEVELOPER_PORTFOLIO_URL', 'https://kaushal-port.netlify.app/'),
    }
    if request.user.is_authenticated:
        # Ensure user has profile and settings safely
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
        context['user_profile'] = profile
        context['user_settings'] = user_settings
    return context
