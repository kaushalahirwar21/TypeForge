import secrets
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .models import EmailOTP

logger = logging.getLogger(__name__)


def generate_otp_code(length=6) -> str:
    """Generate a cryptographically secure numeric OTP."""
    digits = '0123456789'
    return ''.join(secrets.choice(digits) for _ in range(length))


def create_and_send_otp(email: str, purpose: str, user_name: str = None) -> tuple[bool, str]:
    """
    Creates a new 6-digit OTP, saves it to the database, and sends
    a high-contrast, responsive HTML email to the recipient.
    Returns: (success: bool, message: str)
    """
    clean_email = email.strip().lower()
    
    # Invalidate previous unused OTPs for this email and purpose
    EmailOTP.objects.filter(
        email__iexact=clean_email,
        purpose=purpose,
        is_used=False
    ).update(is_used=True)

    # Generate fresh OTP and 10-minute expiry
    code = generate_otp_code(6)
    expires_at = timezone.now() + timedelta(minutes=10)

    EmailOTP.objects.create(
        email=clean_email,
        otp_code=code,
        purpose=purpose,
        expires_at=expires_at,
        is_used=False
    )

    # Prepare Email Content
    display_name = user_name or "Typist"
    if purpose == EmailOTP.PURPOSE_SIGNUP:
        subject = f"{code} is your TypeForge verification code"
        title = "Verify Your Email Address"
        subtitle = "Thank you for creating an account on TypeForge! Enter the verification code below to activate your account and start your touch-typing journey."
        action_label = "Account Registration OTP"
    else:
        subject = f"{code} is your TypeForge password reset code"
        title = "Reset Your Password"
        subtitle = "We received a request to reset the password for your TypeForge account. Enter this code on the password reset page to choose a new password."
        action_label = "Password Reset OTP"

    # Plain text version
    text_content = f"""
Hello {display_name},

{title}
{subtitle}

Your 6-digit verification code is: {code}

This code is valid for 10 minutes. If you did not make this request, you can safely ignore this email.

Happy Typing,
The TypeForge Team
https://typeforge.ai
"""

    # Spaced code display for visual punch
    spaced_code = "  ".join(list(code))

    # Responsive Branded HTML Email
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  body {{ margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #e2e8f0; }}
  .container {{ max-width: 560px; margin: 40px auto; background-color: #1e293b; border-radius: 16px; overflow: hidden; border: 1px solid rgba(148, 163, 184, 0.15); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }}
  .header {{ background: linear-gradient(135deg, #0284c7 0%, #3b82f6 50%, #6366f1 100%); padding: 32px 24px; text-align: center; }}
  .header h1 {{ margin: 0; font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; text-transform: uppercase; }}
  .header p {{ margin: 6px 0 0 0; color: rgba(255, 255, 255, 0.85); font-size: 13px; font-weight: 500; letter-spacing: 1px; }}
  .content {{ padding: 36px 32px; }}
  .greeting {{ font-size: 18px; font-weight: 600; color: #f8fafc; margin-bottom: 12px; }}
  .description {{ font-size: 14px; line-height: 1.6; color: #94a3b8; margin-bottom: 28px; }}
  .badge-container {{ text-align: center; margin: 32px 0; }}
  .badge-label {{ display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #38bdf8; margin-bottom: 10px; }}
  .otp-box {{ background-color: #0f172a; border: 2px dashed #38bdf8; border-radius: 12px; padding: 18px 24px; font-size: 34px; font-weight: 800; letter-spacing: 12px; color: #38bdf8; text-align: center; font-family: 'Courier New', Courier, monospace; display: inline-block; }}
  .expiry-note {{ font-size: 13px; color: #f59e0b; text-align: center; margin-top: 14px; font-weight: 500; }}
  .security-box {{ background-color: rgba(15, 23, 42, 0.6); border-left: 4px solid #6366f1; padding: 14px 18px; border-radius: 6px; margin: 28px 0 10px 0; font-size: 12.5px; line-height: 1.5; color: #94a3b8; }}
  .footer {{ background-color: #0f172a; padding: 22px 24px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid rgba(148, 163, 184, 0.1); }}
  .footer a {{ color: #38bdf8; text-decoration: none; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>TypeForge</h1>
    <p>MASTER TOUCH TYPING</p>
  </div>
  <div class="content">
    <div class="greeting">Hello {display_name},</div>
    <div class="description">{subtitle}</div>
    
    <div class="badge-container">
      <div class="badge-label">{action_label}</div><br>
      <div class="otp-box">{code}</div>
      <div class="expiry-note">&#9201; This code expires in <strong>10 minutes</strong>.</div>
    </div>
    
    <div class="security-box">
      <strong>Security Notice:</strong> Never share this verification code with anyone. TypeForge team members will never ask for your code. If you did not request this, please ignore this email.
    </div>
  </div>
  <div class="footer">
    &copy; {timezone.now().year} TypeForge &bull; Professional Touch Typing Platform<br>
    <a href="https://typeforge.ai">https://typeforge.ai</a>
  </div>
</div>
</body>
</html>"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[clean_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True, "Verification email dispatched successfully."
    except Exception as e:
        logger.error(f"Failed to send OTP email to {clean_email}: {e}")
        # In development console backend, it won't fail; if SMTP fails, return error message
        return False, str(e)


def verify_otp_code(email: str, otp_code: str, purpose: str) -> tuple[bool, str]:
    """
    Validates the provided OTP code against the latest valid code in database.
    Marks OTP as used upon successful verification.
    """
    clean_email = email.strip().lower()
    clean_code = otp_code.strip()

    if not clean_code or len(clean_code) != 6 or not clean_code.isdigit():
        return False, "Please enter a valid 6-digit numeric OTP code."

    otp_record = EmailOTP.objects.filter(
        email__iexact=clean_email,
        purpose=purpose,
        is_used=False
    ).order_by('-created_at').first()

    if not otp_record:
        return False, "No active OTP found. Please request a new verification code."

    if not otp_record.is_valid():
        return False, "This OTP has expired. Please request a new verification code."

    if otp_record.otp_code != clean_code:
        return False, "Incorrect OTP code. Please double-check and try again."

    # Mark as used so it cannot be reused
    otp_record.is_used = True
    otp_record.save(update_fields=['is_used'])
    return True, "OTP verified successfully."
