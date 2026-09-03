import smtplib
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from ..core.config import settings

logger = logging.getLogger(__name__)


def _dispatch_email(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: str,
    dev_log_info: str = "",
) -> bool:
    """
    Central email dispatcher.
    1. If SMTP settings are missing, operates in DEV MODE (logs message and returns True).
    2. If Resend API key is detected, attempts HTTPS REST API delivery (bypassing Render SMTP blocks).
    3. Falls back to standard SMTP over port 587/465.
    """
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(f"[DEV MODE] SMTP not configured. Email to {to_email} ({subject}):\n{dev_log_info or text_content}")
        return True

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    from_header = f"{settings.SMTP_FROM_NAME} <{from_email}>"

    # Attempt 1: Resend HTTPS REST API (bypasses cloud hosting SMTP port 587 blocks)
    is_resend = (
        (settings.SMTP_PASSWORD and settings.SMTP_PASSWORD.startswith("re_"))
        or (settings.SMTP_HOST and "resend.com" in settings.SMTP_HOST.lower())
    )
    if is_resend:
        try:
            with httpx.Client(timeout=15.0) as client:
                resend_resp = client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.SMTP_PASSWORD}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": from_header,
                        "to": [to_email],
                        "subject": subject,
                        "text": text_content,
                        "html": html_content,
                    },
                )
                if resend_resp.status_code in (200, 201):
                    logger.info(f"Successfully dispatched '{subject}' to {to_email} via Resend HTTPS REST API")
                    return True
                else:
                    logger.warning(
                        f"Resend REST API returned HTTP {resend_resp.status_code}: {resend_resp.text}. Trying SMTP fallback..."
                    )
        except Exception as e:
            logger.warning(f"Resend REST API request failed ({e}). Trying SMTP fallback...")

    # Attempt 2: Standard SMTP socket delivery
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_header
    msg["To"] = to_email

    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    msg.attach(part1)
    msg.attach(part2)

    try:
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
            if settings.SMTP_TLS:
                server.ehlo()
                server.starttls()
                server.ehlo()

        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        logger.info(f"Successfully sent '{subject}' to {to_email} via SMTP")
        return True
    except Exception as e:
        logger.error(f"Failed to send '{subject}' to {to_email} via SMTP: {e}")
        return False


def send_registration_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Send a branded 6-digit OTP email for new account registration verification.
    """
    subject = f"{otp_code} is your ExpenseFlow verification code ✉️"

    text_content = f"""Hello,

Thank you for starting your registration on ExpenseFlow!

Your 6-digit verification code is: {otp_code}

Please enter this verification code on the registration page to verify your email and complete your profile.
This code is valid for 10 minutes.

If you did not request this registration code, you can safely ignore this email.

Best regards,
The ExpenseFlow Team
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 20px; padding: 40px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); }}
    .logo {{ text-align: center; margin-bottom: 24px; }}
    .logo h2 {{ margin: 0; color: #4f46e5; font-size: 26px; font-weight: 900; letter-spacing: -0.5px; }}
    .title {{ font-size: 22px; font-weight: 800; color: #0f172a; text-align: center; margin-bottom: 8px; }}
    .subtitle {{ font-size: 14px; color: #64748b; text-align: center; margin-bottom: 28px; }}
    .text {{ font-size: 15px; line-height: 1.6; color: #475569; margin-bottom: 20px; }}
    .otp-box {{ background: #f5f3ff; border: 2px dashed #818cf8; border-radius: 16px; padding: 24px; text-align: center; margin: 28px 0; }}
    .otp-code {{ font-size: 38px; font-weight: 900; letter-spacing: 10px; color: #4f46e5; margin: 0; font-family: 'Courier New', Courier, monospace; }}
    .otp-hint {{ font-size: 12px; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; }}
    .note {{ font-size: 13px; color: #64748b; text-align: center; margin: 20px 0 0 0; line-height: 1.5; }}
    .footer {{ border-top: 1px solid #f1f5f9; padding-top: 24px; margin-top: 32px; font-size: 12px; color: #94a3b8; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <h2>ExpenseFlow</h2>
    </div>
    <div class="title">Verify Your Email Address</div>
    <div class="subtitle">Step 2: Enter your 6-digit confirmation code</div>
    <p class="text">
      Welcome! Please use the 6-digit verification code below to confirm your email and proceed to completing your account profile:
    </p>
    <div class="otp-box">
      <div class="otp-code">{otp_code}</div>
      <div class="otp-hint">Valid for 10 minutes</div>
    </div>
    <p class="note">
      If you did not request this verification code, no account has been created and you can safely ignore this email.
    </p>
    <div class="footer">
      <p style="margin: 0;">&copy; ExpenseFlow &bull; Private & Secure Financial Management</p>
    </div>
  </div>
</body>
</html>
"""

    return _dispatch_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        dev_log_info=f"OTP Code: {otp_code}",
    )


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Send a branded password reset email.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    subject = "Reset Your ExpenseFlow Password"

    text_content = f"""Hello,

We received a request to reset your ExpenseFlow account password.

Click the link below to choose a new password (valid for 60 minutes):
{reset_url}

If you did not request this password reset, you can safely ignore this email.

Best regards,
The ExpenseFlow Team
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; padding: 40px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); }}
    .logo {{ text-align: center; margin-bottom: 24px; }}
    .logo h2 {{ margin: 0; color: #4f46e5; font-size: 26px; font-weight: 900; letter-spacing: -0.5px; }}
    .title {{ font-size: 24px; font-weight: 800; color: #0f172a; text-align: center; margin-bottom: 12px; }}
    .text {{ font-size: 15px; line-height: 1.6; color: #475569; margin-bottom: 28px; text-align: center; }}
    .btn-container {{ text-align: center; margin-bottom: 32px; }}
    .btn {{ display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: #ffffff !important; font-weight: 700; font-size: 15px; padding: 14px 32px; text-decoration: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }}
    .footer {{ border-top: 1px solid #f1f5f9; padding-top: 20px; font-size: 12px; color: #94a3b8; text-align: center; }}
    .fallback-url {{ word-break: break-all; color: #6366f1; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <h2>ExpenseFlow</h2>
    </div>
    <div class="title">Reset Your Password</div>
    <p class="text">
      We received a request to reset the password for your ExpenseFlow account. Click the button below to set a new password.
    </p>
    <div class="btn-container">
      <a href="{reset_url}" class="btn" target="_blank">Reset Password</a>
    </div>
    <p class="text" style="font-size: 13px; color: #64748b; margin-bottom: 8px;">
      This link will expire in <strong>60 minutes</strong>. If you didn't request this change, please ignore this email.
    </p>
    <div class="footer">
      <p style="margin: 0 0 8px 0;">If the button doesn't work, copy and paste this URL into your browser:</p>
      <a href="{reset_url}" class="fallback-url">{reset_url}</a>
      <p style="margin: 16px 0 0 0;">&copy; ExpenseFlow &bull; Private & Secure Financial Tracking</p>
    </div>
  </div>
</body>
</html>
"""

    return _dispatch_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        dev_log_info=f"Reset URL: {reset_url}",
    )


def send_welcome_email(to_email: str, full_name: Optional[str] = None) -> bool:
    """
    Send a branded welcome email to newly activated users.
    """
    login_url = f"{settings.FRONTEND_URL}/login"
    user_display = full_name.strip() if full_name and full_name.strip() else "there"
    subject = "Welcome to ExpenseFlow! 🎉"

    text_content = f"""Hello {user_display},

Welcome to ExpenseFlow!

Your account has been created successfully. You can now start managing your finances:
- Track daily expenses across payment methods (UPI, Cards, Cash).
- Set monthly and category-specific budget limits.
- Analyze spending habits with visual reports and PDF/CSV exports.

Get started by logging in:
{login_url}

Best regards,
The ExpenseFlow Team
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; padding: 40px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); }}
    .logo {{ text-align: center; margin-bottom: 24px; }}
    .logo h2 {{ margin: 0; color: #4f46e5; font-size: 26px; font-weight: 900; letter-spacing: -0.5px; }}
    .title {{ font-size: 24px; font-weight: 800; color: #0f172a; text-align: center; margin-bottom: 8px; }}
    .subtitle {{ font-size: 15px; color: #64748b; text-align: center; margin-bottom: 28px; }}
    .text {{ font-size: 15px; line-height: 1.6; color: #475569; margin-bottom: 20px; }}
    .features {{ background: #f8fafc; border-radius: 12px; padding: 20px; margin: 24px 0; border: 1px solid #f1f5f9; }}
    .feature-item {{ display: flex; align-items: flex-start; margin-bottom: 12px; font-size: 14px; color: #334155; }}
    .feature-item:last-child {{ margin-bottom: 0; }}
    .btn-container {{ text-align: center; margin: 32px 0 20px 0; }}
    .btn {{ display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: #ffffff !important; font-weight: 700; font-size: 15px; padding: 14px 36px; text-decoration: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }}
    .footer {{ border-top: 1px solid #f1f5f9; padding-top: 20px; font-size: 12px; color: #94a3b8; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <h2>ExpenseFlow</h2>
    </div>
    <div class="title">Welcome to ExpenseFlow! 🎉</div>
    <div class="subtitle">Your personal financial clarity journey starts here</div>
    <p class="text">
      Hi <strong>{user_display}</strong>,<br><br>
      Your account is now ready! Here is what you can do right away:
    </p>
    <div class="features">
      <div class="feature-item">📊 <strong>Track Expenses:</strong> Record daily spends with custom categories & payment tags.</div>
      <div class="feature-item" style="margin-top: 8px;">🎯 <strong>Smart Budgets:</strong> Set monthly thresholds and get real-time alerts.</div>
      <div class="feature-item" style="margin-top: 8px;">📑 <strong>Export Reports:</strong> Generate instant PDF & CSV financial reports anytime.</div>
    </div>
    <div class="btn-container">
      <a href="{login_url}" class="btn" target="_blank">Sign In to Dashboard</a>
    </div>
    <div class="footer">
      <p style="margin: 0;">&copy; ExpenseFlow &bull; Private & Secure Financial Tracking</p>
    </div>
  </div>
</body>
</html>
"""

    return _dispatch_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        dev_log_info=f"Login URL: {login_url}",
    )


def send_verification_email(to_email: str, verification_token: str, full_name: Optional[str] = None) -> bool:
    """
    Backwards-compatible email verification link sender.
    """
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    user_display = full_name.strip() if full_name and full_name.strip() else "there"
    subject = "Verify Your ExpenseFlow Account ✉️"

    text_content = f"""Hello {user_display},

Thank you for registering on ExpenseFlow!

Please click the link below to verify your email address and activate your account (valid for 24 hours):
{verify_url}

If you did not register for an ExpenseFlow account, please ignore this email.

Best regards,
The ExpenseFlow Team
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; padding: 40px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); }}
    .logo {{ text-align: center; margin-bottom: 24px; }}
    .logo h2 {{ margin: 0; color: #4f46e5; font-size: 26px; font-weight: 900; letter-spacing: -0.5px; }}
    .title {{ font-size: 24px; font-weight: 800; color: #0f172a; text-align: center; margin-bottom: 8px; }}
    .subtitle {{ font-size: 15px; color: #64748b; text-align: center; margin-bottom: 28px; }}
    .text {{ font-size: 15px; line-height: 1.6; color: #475569; margin-bottom: 20px; }}
    .btn-container {{ text-align: center; margin: 32px 0; }}
    .btn {{ display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: #ffffff !important; font-weight: 700; font-size: 15px; padding: 14px 36px; text-decoration: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }}
    .footer {{ border-top: 1px solid #f1f5f9; padding-top: 20px; font-size: 12px; color: #94a3b8; text-align: center; }}
    .fallback-url {{ word-break: break-all; color: #6366f1; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <h2>ExpenseFlow</h2>
    </div>
    <div class="title">Verify Your Email Address ✉️</div>
    <div class="subtitle">Complete your registration to get started</div>
    <p class="text">
      Hi <strong>{user_display}</strong>,<br><br>
      Thank you for creating an account on ExpenseFlow. Click the button below to verify your email address.
    </p>
    <div class="btn-container">
      <a href="{verify_url}" class="btn" target="_blank">Verify My Email</a>
    </div>
    <div class="footer">
      <p style="margin: 0 0 8px 0;">If the button doesn't work, copy and paste this URL into your browser:</p>
      <a href="{verify_url}" class="fallback-url">{verify_url}</a>
      <p style="margin: 16px 0 0 0;">&copy; ExpenseFlow &bull; Private & Secure Financial Tracking</p>
    </div>
  </div>
</body>
</html>
"""

    return _dispatch_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        dev_log_info=f"Verify URL: {verify_url}",
    )
