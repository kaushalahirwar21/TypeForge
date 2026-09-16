from .models import UserProfile, UserSettings

def site_settings(request):
    """Context processor providing universal TypeForge context across all templates."""
    context = {
        'SITE_NAME': 'TypeForge',
        'SITE_TAGLINE': 'Master Touch Typing with Precision & Speed',
    }
    if request.user.is_authenticated:
        # Ensure user has profile and settings safely
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        settings, _ = UserSettings.objects.get_or_create(user=request.user)
        context['user_profile'] = profile
        context['user_settings'] = settings
    return context
