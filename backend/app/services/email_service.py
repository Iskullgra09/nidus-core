from email.message import EmailMessage
from urllib.parse import urljoin

import aiosmtplib

from app.core.config import settings
from app.core.i18n.service import i18n


class EmailService:
    @staticmethod
    async def _send_email(to_email: str, subject: str, text_content: str, html_content: str) -> None:
        """
        Core async function to send emails via SMTP.
        Falls back to a styled terminal print if SMTP variables are not set (Great for local dev).
        """
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print("\n" + "=" * 60)
            print(f" MOCK EMAIL DISPATCHED TO : {to_email}")
            print("-" * 60)
            print(f" SUBJECT : {subject}")
            print("-" * 60)
            print(f"{text_content}")
            print("=" * 60 + "\n")
            return

        message = EmailMessage()
        message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(text_content)
        message.add_alternative(html_content, subtype="html")

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
                timeout=10,
            )
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")

    @staticmethod
    async def send_invitation_email(email: str, token: str, lang: str = "en") -> None:
        """
        Constructs and sends a localized workspace invitation email.
        """
        frontend_str = str(settings.FRONTEND_URL)
        base_url = frontend_str if frontend_str.endswith("/") else f"{frontend_str}/"
        invite_link = urljoin(base_url, f"invite?token={token}")

        subject = i18n.t("email.invitation_subject", lang=lang)
        body_text = i18n.t("email.invitation_body", lang=lang, link=invite_link)

        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2>Nidus Workspace</h2>
                <p>{body_text.replace(invite_link, f'<a href="{invite_link}">{invite_link}</a>')}</p>
            </body>
        </html>
        """

        await EmailService._send_email(email, subject, body_text, body_html)

    @staticmethod
    async def send_password_reset_email(email: str, token: str, lang: str = "en") -> None:
        """
        Constructs and sends a localized password reset email.
        """
        frontend_str = str(settings.FRONTEND_URL)
        base_url = frontend_str if frontend_str.endswith("/") else f"{frontend_str}/"
        reset_link = urljoin(base_url, f"reset-password?token={token}")

        subject = i18n.t("email.password_reset_subject", lang=lang)
        body_text = i18n.t("email.password_reset_body", lang=lang, link=reset_link)

        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2>Nidus Security</h2>
                <p>{body_text.replace(reset_link, f'<a href="{reset_link}">{reset_link}</a>')}</p>
                <p><small>If you did not request this, please ignore this email. The link will expire in 15 minutes.</small></p>
            </body>
        </html>
        """

        await EmailService._send_email(email, subject, body_text, body_html)
