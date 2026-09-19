import logging
import secrets
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from .models import EmailOTP

logger = logging.getLogger(__name__)

RESEND_COOLDOWN_SECONDS = 60
MAX_FAILED_ATTEMPTS = 5
OTP_EXPIRY_MINUTES = 10


def generate_otp_code(length: int = 6) -> str:
    """Generate a cryptographically secure numeric OTP."""
    digits = '0123456789'
    return ''.join(secrets.choice(digits) for _ in range(length))


def can_request_otp(email: str, purpose: str) -> tuple[bool, int]:
    """
    Rate limiting / cooldown check:
    Ensures users cannot request another OTP within 60 seconds for the same email and purpose.
    Returns: (can_request: bool, wait_seconds_remaining: int)
    """
    clean_email = email.strip().lower()
    cooldown_threshold = timezone.now() - timedelta(seconds=RESEND_COOLDOWN_SECONDS)
    
    recent_otp = EmailOTP.objects.filter(
        email__iexact=clean_email,
        purpose=purpose,
        created_at__gte=cooldown_threshold
    ).order_by('-created_at').first()

    if recent_otp:
        elapsed = (timezone.now() - recent_otp.created_at).total_seconds()
        remaining = max(1, int(RESEND_COOLDOWN_SECONDS - elapsed))
        return False, remaining

    return True, 0


def create_and_send_otp(email: str, purpose: str, user_name: str = None) -> tuple[bool, str]:
    """
    Generates a secure 6-digit OTP, saves it with a 10-minute expiry,
    and sends a branded authentication email using the configured email account.
    Returns: (success: bool, user_message: str)
    """
    clean_email = email.strip().lower()

    # Rate limiting / cooldown check
    can_request, wait_seconds = can_request_otp(clean_email, purpose)
    if not can_request:
        return False, f"Please wait {wait_seconds} seconds before requesting a new verification code."

    # Invalidate previous unused OTPs for this email and purpose
    EmailOTP.objects.filter(
        email__iexact=clean_email,
        purpose=purpose,
        is_used=False
    ).update(is_used=True)

    # Generate fresh secure OTP and 10-minute expiry
    code = generate_otp_code(6)
    expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    EmailOTP.objects.create(
        email=clean_email,
        otp_code=code,
        purpose=purpose,
        expires_at=expires_at,
        is_used=False,
        failed_attempts=0
    )

    # Email content configuration
    display_name = user_name or "Typist"
    if purpose == EmailOTP.PURPOSE_SIGNUP:
        subject = "Verify your TypeRise account"
        title = "Verify your TypeRise account"
        subtitle = "Thank you for creating an account on TypeRise! Enter the verification code below to activate your account and start practicing."
        action_label = "Account Verification Code"
    else:
        subject = "Reset your TypeRise password"
        title = "Reset your TypeRise password"
        subtitle = "We received a request to reset the password for your TypeRise account. Enter the verification code below to set a new password."
        action_label = "Password Reset Code"

    # Plain text email content
    text_content = f"""Hello {display_name},

{title}
{subtitle}

Your verification code is: {code}

This code expires in {OTP_EXPIRY_MINUTES} minutes.

Security Notice: If you did not make this request, please ignore this email. Never share your verification code with anyone.

Best regards,
The TypeRise Team
https://typerise.ai
"""

    # Responsive HTML email
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{ margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #e2e8f0; }}
  .container {{ max-width: 540px; margin: 36px auto; background-color: #1e293b; border-radius: 16px; overflow: hidden; border: 1px solid rgba(148, 163, 184, 0.15); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }}
  .header {{ background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #4f46e5 100%); padding: 32px 24px; text-align: center; }}
  .header h1 {{ margin: 0; font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; }}
  .header p {{ margin: 6px 0 0 0; color: rgba(255, 255, 255, 0.9); font-size: 13px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }}
  .content {{ padding: 36px 32px; }}
  .greeting {{ font-size: 18px; font-weight: 600; color: #f8fafc; margin-bottom: 12px; }}
  .description {{ font-size: 14.5px; line-height: 1.6; color: #94a3b8; margin-bottom: 26px; }}
  .badge-container {{ text-align: center; margin: 30px 0; }}
  .badge-label {{ display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #38bdf8; margin-bottom: 10px; }}
  .otp-box {{ background-color: #0f172a; border: 2px dashed #38bdf8; border-radius: 12px; padding: 18px 24px; font-size: 34px; font-weight: 800; letter-spacing: 10px; color: #38bdf8; text-align: center; font-family: 'Courier New', Courier, monospace; display: inline-block; }}
  .expiry-note {{ font-size: 13px; color: #f59e0b; text-align: center; margin-top: 14px; font-weight: 500; }}
  .security-box {{ background-color: rgba(15, 23, 42, 0.6); border-left: 4px solid #38bdf8; padding: 14px 18px; border-radius: 6px; margin: 28px 0 10px 0; font-size: 12.5px; line-height: 1.5; color: #94a3b8; }}
  .footer {{ background-color: #0f172a; padding: 22px 24px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid rgba(148, 163, 184, 0.1); }}
  .footer a {{ color: #38bdf8; text-decoration: none; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>TypeRise</h1>
    <p>Learn Typing Faster</p>
  </div>
  <div class="content">
    <div class="greeting">Hello {display_name},</div>
    <div class="description">{subtitle}</div>
    
    <div class="badge-container">
      <div class="badge-label">{action_label}</div><br>
      <div class="otp-box">{code}</div>
      <div class="expiry-note">&#9201; This code expires in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</div>
    </div>
    
    <div class="security-box">
      <strong>Security Notice:</strong> Never share this verification code with anyone. TypeRise team members will never ask for your code. If you did not request this, you can safely ignore this email.
    </div>
  </div>
  <div class="footer">
    &copy; {timezone.now().year} TypeRise &bull; Professional Touch Typing Platform<br>
    <a href="https://typerise.ai">https://typerise.ai</a>
  </div>
</div>
</body>
</html>"""

    # Dispatch using the user's configured email account
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[clean_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True, "Verification email sent successfully."
    except Exception as e:
        # Safe server logging without exposing credentials or OTP
        logger.error(f"Failed to dispatch authentication email for {purpose} to {clean_email}: {type(e).__name__}")
        return False, "Unable to send the email right now. Please try again later."


def verify_otp_code(email: str, otp_code: str, purpose: str) -> tuple[bool, str]:
    """
    Validates the provided OTP code against the latest valid code in database.
    - Constant-time comparison
    - Expiration check (10 min)
    - Failed attempts limit (max 5)
    - Invalidation upon successful use
    Returns: (is_valid: bool, message: str)
    """
    clean_email = email.strip().lower()
    clean_code = otp_code.strip()

    if not clean_code or len(clean_code) != 6 or not clean_code.isdigit():
        return False, "Please enter a valid 6-digit numeric verification code."

    otp_record = EmailOTP.objects.filter(
        email__iexact=clean_email,
        purpose=purpose,
        is_used=False
    ).order_by('-created_at').first()

    if not otp_record:
        return False, "No active verification code found. Please request a new code."

    # Check if locked out due to failed attempts
    if otp_record.failed_attempts >= MAX_FAILED_ATTEMPTS:
        otp_record.is_used = True
        otp_record.save(update_fields=['is_used'])
        return False, "Too many incorrect attempts. For your security, this code has been invalidated. Please request a new code."

    # Check expiration
    if timezone.now() > otp_record.expires_at:
        return False, "This verification code has expired. Please request a new code."

    # Constant-time comparison
    if not secrets.compare_digest(otp_record.otp_code, clean_code):
        otp_record.failed_attempts += 1
        if otp_record.failed_attempts >= MAX_FAILED_ATTEMPTS:
            otp_record.is_used = True
            otp_record.save(update_fields=['failed_attempts', 'is_used'])
            return False, "Too many incorrect attempts. This code has been invalidated. Please request a new code."
        otp_record.save(update_fields=['failed_attempts'])
        remaining = MAX_FAILED_ATTEMPTS - otp_record.failed_attempts
        return False, f"Incorrect verification code. {remaining} attempt{'s' if remaining != 1 else ''} remaining."

    # Invalidate OTP upon successful verification
    otp_record.is_used = True
    otp_record.save(update_fields=['is_used'])
    return True, "Verification successful."
