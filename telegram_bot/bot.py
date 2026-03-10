import os
import requests


def send_job_alert(job):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    channel_id = os.environ.get('TELEGRAM_CHANNEL_ID', '')

    if not bot_token or not channel_id:
        print("Telegram bot not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID.")
        return False

    message = f"""🔔 *New Job Alert*

📋 *{job.title}*
🏢 Organization: {job.organization}
📊 Total Posts: {job.total_posts or 'Check Notification'}
📅 Last Date: {job.last_date or 'Check Notification'}
📍 State: {job.state or 'All India'}
🎓 Qualification: {job.qualification or 'Check Notification'}

🔗 [Apply Now]({job.apply_link})
📄 [View Notification]({job.notification_link})

👉 @IndiaJobPortal"""

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': channel_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"Telegram alert sent for: {job.title}")
            return True
        else:
            print(f"Telegram error: {response.text}")
            return False
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False


def send_custom_message(message_text):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    channel_id = os.environ.get('TELEGRAM_CHANNEL_ID', '')

    if not bot_token or not channel_id:
        return False

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': channel_id,
            'text': message_text,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False
