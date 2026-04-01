import asyncio
from urllib.parse import urljoin

from app.core.config import settings
from app.core.i18n.service import i18n


class EmailService:
    @staticmethod
    async def send_invitation_email(email: str, token: str, lang: str = "en") -> None:
        """
        Simulates sending a localized email with a safely constructed URL.
        """
        await asyncio.sleep(2)

        frontend_str = str(settings.FRONTEND_URL)

        base_url = frontend_str if frontend_str.endswith("/") else f"{frontend_str}/"

        invite_link = urljoin(base_url, f"invite?token={token}")

        subject = i18n.t("email.invitation_subject", lang=lang)
        body = i18n.t("email.invitation_body", lang=lang, link=invite_link)

        print("\n" + "=" * 60)
        print(f" DISPATCHING EMAIL TO : {email}")
        print(f" LANGUAGE SPECIFIED : {lang.upper()}")
        print("-" * 60)
        print(f" SUBJECT : {subject}")
        print("-" * 60)
        print(f"{body}")
        print("=" * 60 + "\n")
