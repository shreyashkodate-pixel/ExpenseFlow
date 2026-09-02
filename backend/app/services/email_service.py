import smtplib
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Send a branded password reset email via SMTP.
    If SMTP is not configured, logs the reset link for local testing and returns True.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(
            f"[DEV MODE] SMTP not configured. Password reset link for {to_email}:\n{reset_url}"
        )
        return True

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    from_header = f"{settings.SMTP_FROM_NAME} <{from_email}>"

    # Create message container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset Your ExpenseFlow Password"
    msg["From"] = from_header
    msg["To"] = to_email

    # Plain text version
    text_content = f"""Hello,

We received a request to reset your ExpenseFlow account password.

Click the link below to choose a new password (valid for 60 minutes):
{reset_url}

If you did not request this password reset, you can safely ignore this email.

Best regards,
The ExpenseFlow Team
"""

    # Rich HTML version
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; padding: 40px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); }}
    .logo {{ text-align: center; margin-bottom: 24px; }}
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
      <h2 style="margin: 0; color: #4f46e5; font-size: 26px; font-weight: 900; letter-spacing: -0.5px;">ExpenseFlow</h2>
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
        logger.info(f"Successfully sent password reset email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email} via SMTP: {e}")
        return False


def send_welcome_email(to_email: str, full_name: Optional[str] = None) -> bool:
    """
    Send a branded welcome email to newly registered users via SMTP.
    If SMTP is not configured, logs the welcome dispatch for local testing and returns True.
    """
    login_url = f"{settings.FRONTEND_URL}/login"
    user_display = full_name.strip() if full_name and full_name.strip() else "there"

    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(
            f"[DEV MODE] SMTP not configured. Welcome email for {to_email} (Name: {user_display}). Login link: {login_url}"
        )
        return True

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    from_header = f"{settings.SMTP_FROM_NAME} <{from_email}>"

    # Create message container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Welcome to ExpenseFlow! 🎉"
    msg["From"] = from_header
    msg["To"] = to_email

    # Plain text version
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

    # Rich HTML version
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; padding: 40px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); }}
    .logo {{ text-align: center; margin-bottom: 24px; }}
    .title {{ font-size: 24px; font-weight: 800; color: #0f172a; text-align: center; margin-bottom: 8px; }}
    .subtitle {{ font-size: 15px; color: #64748b; text-align: center; margin-bottom: 28px; }}
    .text {{ font-size: 15px; line-height: 1.6; color: #475569; margin-bottom: 20px; }}
    .feature-box {{ background-color: #f8fafc; border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; border: 1px solid #f1f5f9; }}
    .feature-item {{ font-size: 14px; color: #334155; margin-bottom: 10px; display: flex; align-items: center; }}
    .feature-item:last-child {{ margin-bottom: 0; }}
    .btn-container {{ text-align: center; margin: 32px 0; }}
    .btn {{ display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: #ffffff !important; font-weight: 700; font-size: 15px; padding: 14px 36px; text-decoration: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }}
    .footer {{ border-top: 1px solid #f1f5f9; padding-top: 20px; font-size: 12px; color: #94a3b8; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <h2 style="margin: 0; color: #4f46e5; font-size: 26px; font-weight: 900; letter-spacing: -0.5px;">ExpenseFlow</h2>
    </div>
    <div class="title">Welcome to ExpenseFlow! 🎉</div>
    <div class="subtitle">Smart, effortless financial tracking</div>
    <p class="text">
      Hi <strong>{user_display}</strong>,
    </p>
    <p class="text">
      Thank you for joining ExpenseFlow! Your account has been registered successfully. You're all set to take control of your financial journey.
    </p>
    <div class="feature-box">
      <div class="feature-item">📊 &nbsp;<strong>Track Expenses:</strong> Categorize daily transactions by cash, card, or UPI.</div>
      <div class="feature-item">🎯 &nbsp;<strong>Set Budgets:</strong> Create monthly spending limits and avoid overspending.</div>
      <div class="feature-item">📈 &nbsp;<strong>Visual Analytics:</strong> View spending breakdowns and export PDF/CSV reports.</div>
    </div>
    <div class="btn-container">
      <a href="{login_url}" class="btn" target="_blank">Go to ExpenseFlow</a>
    </div>
    <div class="footer">
      <p style="margin: 0 0 8px 0;">Need assistance? Simply reply to this email or visit our help center.</p>
      <p style="margin: 8px 0 0 0;">&copy; ExpenseFlow &bull; Private & Secure Financial Tracking</p>
    </div>
  </div>
</body>
</html>
"""

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
        logger.info(f"Successfully sent welcome email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email} via SMTP: {e}")
        return False


def send_verification_email(to_email: str, verification_token: str, full_name: Optional[str] = None) -> bool:
    """
    Send a branded email verification link to newly registered users via SMTP.
    If SMTP is not configured, logs the verification link for local testing and returns True.
    """
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    user_display = full_name.strip() if full_name and full_name.strip() else "there"

    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(
            f"[DEV MODE] SMTP not configured. Verification link for {to_email} (Name: {user_display}):\n{verify_url}"
        )
        return True

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    from_header = f"{settings.SMTP_FROM_NAME} <{from_email}>"

    # Create message container
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify Your ExpenseFlow Account ✉️"
    msg["From"] = from_header
    msg["To"] = to_email

    # Plain text version
    text_content = f"""Hello {user_display},

Thank you for registering on ExpenseFlow!

Please click the link below to verify your email address and activate your account (valid for 24 hours):
{verify_url}

If you did not register for an ExpenseFlow account, please ignore this email.

Best regards,
The ExpenseFlow Team
"""

    # Rich HTML version
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 20px; padding: 40px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); }}
    .logo {{ text-align: center; margin-bottom: 24px; }}
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
      <h2 style="margin: 0; color: #4f46e5; font-size: 26px; font-weight: 900; letter-spacing: -0.5px;">ExpenseFlow</h2>
    </div>
    <div class="title">Verify Your Email Address ✉️</div>
    <div class="subtitle">Complete your registration to get started</div>
    <p class="text">
      Hi <strong>{user_display}</strong>,
    </p>
    <p class="text">
      Thank you for creating an account on ExpenseFlow. To activate your account and start tracking your finances, please click the button below to verify your email address.
    </p>
    <div class="btn-container">
      <a href="{verify_url}" class="btn" target="_blank">Verify My Email</a>
    </div>
    <p class="text" style="font-size: 13px; color: #64748b; text-align: center; margin-bottom: 8px;">
      This verification link is valid for <strong>24 hours</strong>. If you didn't create an account, you can safely ignore this email.
    </p>
    <div class="footer">
      <p style="margin: 0 0 8px 0;">If the button doesn't work, copy and paste this URL into your browser:</p>
      <a href="{verify_url}" class="fallback-url">{verify_url}</a>
      <p style="margin: 16px 0 0 0;">&copy; ExpenseFlow &bull; Private & Secure Financial Tracking</p>
    </div>
  </div>
</body>
</html>
"""

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
        logger.info(f"Successfully sent email verification email to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email verification email to {to_email} via SMTP: {e}")
        return False

