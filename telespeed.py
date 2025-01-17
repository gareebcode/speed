from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, PhoneCodeInvalidError
import os

# Default API credentials
DEFAULT_API_ID = 19748984  # Replace with your default API ID
DEFAULT_API_HASH = "2141e30f96dfbd8c46fbb5ff4b197004"  # Replace with your default API HASH
BOT_TOKEN = "7326914757:AAGukO4Yx1LPV9eTZ69oIun1y-SlMDmo7yI"

# Create a bot client
bot = TelegramClient("bot", DEFAULT_API_ID, DEFAULT_API_HASH).start(bot_token=BOT_TOKEN)

# Temporary data storage for user sessions
user_sessions = {}

# Start command handler
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.sender_id
    user_sessions.pop(user_id, None)  # Clear previous session data
    await event.reply(
        "Welcome to the Session String Generator bot! Send your phone number in the format:\n\n`+1234567890`"
    )

# Generic message handler
@bot.on(events.NewMessage)
async def handle_message(event):
    user_id = event.sender_id
    user_message = event.text.strip()

    # Handle phone number input
    if user_id not in user_sessions:
        if not user_message.startswith("+"):
            return await event.reply("Invalid phone number format! Please use: `+1234567890`")

        # Start login process
        user_sessions[user_id] = {"phone": user_message}
        client = TelegramClient(f"session_{user_id}", DEFAULT_API_ID, DEFAULT_API_HASH)
        user_sessions[user_id]["client"] = client

        try:
            await client.connect()
            await client.send_code_request(user_message)
            await event.reply("Code sent to your phone. Reply with the code. Send with spaces")
        except PhoneNumberInvalidError:
            user_sessions.pop(user_id, None)
            await event.reply("Invalid phone number! Restart with /start.")
        return

    # Handle code input
    session_data = user_sessions.get(user_id)
    if session_data and "code" not in session_data:
        try:
            code = user_message.replace(" ", "")
            client = session_data["client"]
            await client.sign_in(session_data["phone"], code)
            session_string = client.session.save()
            await event.reply(f"Login successful! Here is your session string:\n\n`{session_string}`\n\nKeep it secure!")
            await client.disconnect()
            user_sessions.pop(user_id, None)
        except PhoneCodeInvalidError:
            await event.reply("Invalid code! Please try again.")
        except SessionPasswordNeededError:
            session_data["code"] = code
            await event.reply("Two-step verification enabled. Send your password (separate words by spaces if applicable).")
        return

    # Handle two-step password
    if session_data and "password" not in session_data:
        try:
            # Remove spaces from password
            password = user_message.replace(" ", "")
            client = session_data["client"]
            await client.sign_in(password=password)
            session_string = client.session.save()
            await event.reply(f"Login successful! Here is your session string:\n\n`{session_string}`\n\nKeep it secure!")
            await client.disconnect()
            user_sessions.pop(user_id, None)
        except Exception as e:
            await event.reply(f"Error during password authentication! Restart with /start.\n\nDetails: {e}")
            user_sessions.pop(user_id, None)
        return

    # Fallback for unrecognized input
    await event.reply("Invalid input! Restart with /start.")

# Start the bot
print("Bot is running...")
bot.run_until_disconnected()
