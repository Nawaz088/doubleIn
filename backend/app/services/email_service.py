import httpx

from app.core.config import settings


async def send_email(
    to: str,
    subject: str,
    text: str,
    html: str | None = None,
    from_name: str | None = None,
) -> bool:
    if not settings.SENDGRID_API_KEY:
        return False

    headers = {
        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "personalizations": [{"to": [{"email": to}]}],
        "from": {"email": "noreply@doublehq.com", "name": from_name or settings.APP_NAME},
        "subject": subject,
        "content": [{"type": "text/plain", "value": text}],
    }

    if html:
        payload["content"].append({"type": "text/html", "value": html})

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers=headers,
                json=payload,
            )
            return resp.status_code in (200, 202)
    except Exception:
        return False


async def send_magic_link(email: str, token: str) -> bool:
    url = f"{settings.MAGIC_LINK_BASE_URL}/magic-link?token={token}"
    return await send_email(
        to=email,
        subject="Your Magic Link to DoubleHQ",
        text=f"Click here to sign in: {url}",
        html=f'<p>Click <a href="{url}">here</a> to sign in to DoubleHQ.</p>',
    )


async def send_password_reset(email: str, token: str) -> bool:
    url = f"{settings.MAGIC_LINK_BASE_URL}/reset-password?token={token}"
    return await send_email(
        to=email,
        subject="Reset your DoubleHQ password",
        text=f"Click here to reset your password: {url}",
        html=f'<p>Click <a href="{url}">here</a> to reset your password.</p>',
    )


async def send_invite_email(email: str, org_name: str, invite_url: str) -> bool:
    return await send_email(
        to=email,
        subject=f"You've been invited to {org_name} on DoubleHQ",
        text=f"You've been invited to join {org_name}. Click here to accept: {invite_url}",
        html=f'<p>You\'ve been invited to join <strong>{org_name}</strong>. Click <a href="{invite_url}">here</a> to accept.</p>',
    )
