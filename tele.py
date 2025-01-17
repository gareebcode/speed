from telethon import TelegramClient, events
from telethon.tl.types import Message
from telethon.sessions import StringSession
from FastTelethonhelper import fast_download
import os

# Replace these with your own values
API_ID = '19748984'
API_HASH = '2141e30f96dfbd8c46fbb5ff4b197004'
SESSION_STRING = "1BVtsOG8BuxskcX5JneBQhJZBazCYc3y-yZn0IE7ZjNz4KH9E8R817Qzttw-Wjh4P1nSRAbcN2icb-BRDhFcm2JKR12kk7xlFSwEKE_T7T3_QV4i_GQB6bOXGFD_nd7aBzQUSWGZV4t21fujl03zOjDrW8v6UGA_4SG1VJ6fbji9ChlgWOV43k3_oc7gkJMGvniShqXh5z5i8JLzCsWe4u0WVkR09rhfd2PEM9hb7UlBCehs0de2UC4X5bG8qULlym3scqctkKVLh0rVNkIlTn3tAWqTzGJr6dRN5UzUkAavUNIDz2MgNqc11zUO0nK0uduoEkc2wRsUMWPsT_2WLl_u3E8jy9_M=
"

# Directory to store downloaded files
DOWNLOAD_DIR = "downloads"

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Initialize the Telegram client using the session string
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def progress_bar_str(downloaded_bytes, total_bytes):
    """
    Formats the progress bar as a string.
    """
    percent = (downloaded_bytes / total_bytes) * 100
    bar_length = 20
    filled_length = int(bar_length * percent // 100)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    return f"[{bar}] {percent:.2f}% ({downloaded_bytes}/{total_bytes})"


@client.on(events.NewMessage(pattern="/get_message"))
async def get_message_handler(event):
    """
    Handles the /get_message command to fetch and download a message by ID.
    Command format: /get_message <chat_id> <message_id>
    """
    try:
        # Parse command arguments
        command = event.raw_text.split()
        if len(command) != 3:
            await event.reply("Usage: /get_message <chat_id> <message_id>")
            return

        chat_id = int(command[1])
        message_id = int(command[2])

        # Fetch the message
        message: Message = await client.get_messages(chat_id, ids=message_id)
        if not message:
            await event.reply("Message not found!")
            return

        # Check if the message has media
        if not message.media:
            await event.reply("No downloadable media found in the message!")
            return

        # Send an initial message to track progress
        progress_message = await event.reply("Starting download...")

        # File download path
        download_path = os.path.join(DOWNLOAD_DIR, f"{chat_id}_{message_id}")

        # Use fast_download with a progress message
        downloaded_file = await fast_download(
            client,
            message,
            reply=progress_message,
            download_folder=DOWNLOAD_DIR,
            progress_bar_function=progress_bar_str,
        )

        # Notify completion
        await progress_message.edit(f"Download complete! File saved at `{downloaded_file}`")

        # Optionally delete the file after sending
        os.remove(downloaded_file)
    except Exception as e:
        await event.reply(f"An error occurred: {str(e)}")


# Start the client
async def main():
    print("Starting client with session string...")
    await client.start()  # No login prompt required
    print("Client is running...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
