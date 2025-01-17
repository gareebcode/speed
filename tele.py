from telethon import TelegramClient, events
from telethon.tl.types import Message
from telethon.sessions import StringSession
from FastTelethonhelper import fast_download
import os
import time

# Replace these with your own values
API_ID = '19748984'
API_HASH = '2141e30f96dfbd8c46fbb5ff4b197004'
SESSION_STRING = "SESSION"

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

user_progress = {}

def progress_callback(done, total, user_id):
    # Check if this user already has progress tracking
    if user_id not in user_progress:
        user_progress[user_id] = {
            'previous_done': 0,
            'previous_time': time.time()
        }
    
    # Retrieve the user's tracking data
    user_data = user_progress[user_id]
    
    # Calculate the percentage of progress
    percent = (done / total) * 100
    
    # Format the progress bar
    completed_blocks = int(percent // 10)
    remaining_blocks = 10 - completed_blocks
    progress_bar = "♦" * completed_blocks + "◇" * remaining_blocks
    
    # Convert done and total to MB for easier reading
    done_mb = done / (1024 * 1024)  # Convert bytes to MB
    total_mb = total / (1024 * 1024)
    
    # Calculate the upload speed (in bytes per second)
    speed = done - user_data['previous_done']
    elapsed_time = time.time() - user_data['previous_time']
    
    if elapsed_time > 0:
        speed_bps = speed / elapsed_time  # Speed in bytes per second
        speed_mbps = (speed_bps * 8) / (1024 * 1024)  # Speed in Mbps
    else:
        speed_mbps = 0
    
    # Estimated time remaining (in seconds)
    if speed_bps > 0:
        remaining_time = (total - done) / speed_bps
    else:
        remaining_time = 0
    
    # Convert remaining time to minutes
    remaining_time_min = remaining_time / 60
    
    # Format the final output as needed
    final = (
        f"╭──────────────────╮\n"
        f"│     **__SpyLib ⚡ Uploader__**       \n"
        f"├──────────\n"
        f"│ {progress_bar}\n\n"
        f"│ **__Progress:__** {percent:.2f}%\n"
        f"│ **__Done:__** {done_mb:.2f} MB / {total_mb:.2f} MB\n"
        f"│ **__Speed:__** {speed_mbps:.2f} Mbps\n"
        f"│ **__ETA:__** {remaining_time_min:.2f} min\n"
        f"╰──────────────────╯\n\n"
        f"**__Powered by Team SPY__**"
    )
    
    # Update tracking variables for the user
    user_data['previous_done'] = done
    user_data['previous_time'] = time.time()
    
    return final

@client.on(events.NewMessage(pattern="/get_message"))
async def get_message_handler(event):
    """
    Handles the /get_message command to fetch and download a message by ID.
    Command format: /get_message <chat_id> <message_id>
    """
    sender = event.sender_id

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
            progress_bar_function=lambda done, total: progress_callback(done, total, sender),
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
