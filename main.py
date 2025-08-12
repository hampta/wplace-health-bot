import os
import time
import json
import requests
import cloudscraper

from dotenv import load_dotenv

load_dotenv()

# Health check configuration
HEALTH_URL = "https://backend.wplace.live/health"
HEALTH_CHECK_INTERVAL = int(os.environ.get("HEALTH_CHECK_INTERVAL", 15))
HEALTH_DATA_FILE = "health_data.json"

# TELEGRAM API configuration
TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}".format
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", None)
TELEGRAM_ACCESS_TOKEN = os.environ.get("TELEGRAM_ACCESS_TOKEN", None)

# DISCORD API configuration
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PING_ROLE_ID = os.environ.get("PING_ROLE_ID")
AVATAR_URL = os.environ.get("AVATAR_URL")

# ensure the environment variables are set
if (
    not WEBHOOK_URL
    or not PING_ROLE_ID
    or not TELEGRAM_ACCESS_TOKEN
    or not TELEGRAM_CHAT_ID
):
    raise ValueError(
        "WEBHOOK_URL, PING_ROLE_ID, TELEGRAM_ACCESS_TOKEN, and TELEGRAM_CHAT_ID must be set in the .env file."
    )

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }
)

# Create a cloudscraper instance
scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance

def save_health_data(data):
    """Save health data to a JSON file."""
    with open(HEALTH_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_health_data():
    """Load health data from a JSON file."""
    if os.path.exists(HEALTH_DATA_FILE):
        with open(HEALTH_DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "UNKNOWN",
    }


# send webhook to Discord
def send_webhook_message(content):
    data = {
        "username": "WPlace Health Bot",
        "avatar_url": AVATAR_URL,
        "content": content,
    }
    response = requests.post(WEBHOOK_URL, json=data)
    return response


def telegram_command(name, data):
    url = TELEGRAM_API(token=TELEGRAM_ACCESS_TOKEN, method=name)
    r = requests.post(url, json=data)
    if r.status_code != 200:
        print(f"Telegram API error: {r.status_code} - {r.text}")

def telegram_sendMessage(text: str, chat_id: str, notify=True):
    return telegram_command(
        "sendMessage",
        {
            "text": text,
            "chat_id": chat_id,
            "parse_mode": "markdown",
            "disable_notification": not notify,
        },
    )

# check health of the backend with up to 5 tries
def check_health():
    try:
        response = scraper.get(HEALTH_URL, timeout=10, allow_redirects=True)
        response.raise_for_status()  # raise an error for bad responses
        print(f"Health check response: {response.status_code}")
        return response.status_code
    except requests.RequestException as e:
        print(f"Health check failed: {e}")
        return 500


# main function to run the health check and send a message
def main():
    while True:
        health_status = check_health()
        health_data = load_health_data()
        # send message if health status has changed
        prev_status = health_data.get("status")
        prev_status_code = health_data.get("health_check_response", 0)
        curr_status = "UP" if health_status == 200 else "DOWN"

        if curr_status != prev_status or prev_status_code == 0:
            content = (
                f"{'🟢' if curr_status == 'UP' else '🔴'} The backend is {curr_status}! (Status code: {health_status})"
            )
        else:
            time.sleep(HEALTH_CHECK_INTERVAL)
            continue

        response = send_webhook_message(f"{content} <@&{PING_ROLE_ID}>")
        if TELEGRAM_CHAT_ID and TELEGRAM_ACCESS_TOKEN:
            telegram_sendMessage(
                text=content,
                chat_id=TELEGRAM_CHAT_ID,
                notify=True,
            )
        else:
            print(
                "Telegram chat ID or access token is not set. Skipping Telegram notification."
            )
        if response.status_code == 204:
            print("Webhook message sent successfully.")
        else:
            print(
                f"Failed to send webhook message. Status code: {response.status_code}"
            )
        save_health_data(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": curr_status,
                "health_check_response": health_status,
            }
        )
        # Wait for a specified interval before the next check
        time.sleep(HEALTH_CHECK_INTERVAL)


if __name__ == "__main__":
    main()
