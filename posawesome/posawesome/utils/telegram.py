import frappe
from frappe.utils import cstr


ERROR_TITLE = "POS Awesome Telegram"


def _get_telegram_credentials():
    """Return bot token and chat id from site config."""
    config = frappe.get_site_config() or {}
    token = config.get("telegram_bot_token")
    chat_id = config.get("telegram_chat_id")
    if not token or not chat_id:
        frappe.log_error(
            "Missing telegram_bot_token or telegram_chat_id in site_config.json",
            ERROR_TITLE,
        )
        return None, None
    return cstr(token).strip(), cstr(chat_id).strip()


def send_telegram_message(message: str) -> None:
    """Send `message` to Telegram using the configured bot credentials."""
    token, chat_id = _get_telegram_credentials()
    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        frappe.make_post_request(url, data=payload)
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"{ERROR_TITLE} sendMessage failed")
