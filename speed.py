import asyncio
from pyrogram import Client, filters

# Replace with your credentials
API_ID = "23037009"
API_HASH = "9a214f65832749215b9532cdb3df73b9"
STRING = 'BQFfhFEAsYi7gsp4rYQc8PMgdl1kjn7ds6sCmuX4OHP2kWJPnqpxK3JvzcFfWjCVhA3pMwUritf2RuZDYISQWzz23avzcOVGGfKmi1vX7hG90Jy7xBVjpTmMFXTXAacdoP2j05pk9uHH_qboM0OMFpQ2M777ycwmN_Dzf0wMuW_qq4nestKNLlGvkIgKPXFi-jgy0RA50XTiEnP8kWZydZxfRbyneHSJ-wZam5hS-3qycKKxj6OIt7onwzC5o6r1jVq-5mo9uQ1_kgAAAAGPgXiWAA'

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, 
session_string=STRING)


@app.on_message(filters.reply & filters.text & filters.regex("^dl$"))
async def trigger_download(client, message):
    # Ensure the replied-to message contains media
    if not message.reply_to_message or not (
        message.reply_to_message.document
        or message.reply_to_message.video
        or message.reply_to_message.audio
    ):
        await message.reply("Please reply to a file (document, video, or audio) with 'dl' to start the download.")
        return

    # Extract media from the replied-to message
    media = (
        message.reply_to_message.document
        or message.reply_to_message.video
        or message.reply_to_message.audio
    )
    file_name = media.file_name or "downloaded_file"
    file_size = media.file_size
    chunk_size = 1024 * 1024  # 1 MiB per chunk
    total_chunks = (file_size + chunk_size - 1) // chunk_size  # Total chunks needed

    await message.reply(f"Downloading {file_name} ({file_size} bytes) in {total_chunks} chunks...")

    # Shared dictionary to store chunks
    chunk_storage = {}

    async def fetch_chunk(offset):
        """Fetch a specific chunk by its offset."""
        try:
            async for chunk in client.stream_media(
                message=media,
                limit=1,  # Always fetch one chunk
                offset=offset,
            ):
                chunk_storage[offset] = chunk
                print(f"Chunk {offset + 1}/{total_chunks} downloaded")
        except Exception as e:
            print(f"Error downloading chunk {offset + 1}: {e}")

    # Create tasks for all chunks
    tasks = [fetch_chunk(offset) for offset in range(total_chunks)]

    # Run tasks concurrently
    await asyncio.gather(*tasks)

    # Write the chunks to the file in order
    with open(file_name, "wb") as file:
        for offset in range(total_chunks):
            if offset in chunk_storage:
                file.write(chunk_storage[offset])
            else:
                print(f"Warning: Missing chunk {offset + 1}")

    await message.reply(f"Download of {file_name} completed!")


app.run()
