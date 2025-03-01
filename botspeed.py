from pyrogram import Client, filters
import asyncio

API_ID = "23037009"
API_HASH = "9a214f65832749215b9532cdb3df73b9"
BOT_TOKEN = "7671721522:AAGZVMjDsgJPHgNjQM"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Semaphore to limit concurrent chunks processing to 5 tasks at once
semaphore = asyncio.Semaphore(5)

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

    # Extract media details
    media = (
        message.reply_to_message.document
        or message.reply_to_message.video
        or message.reply_to_message.audio
    )
    file_name = media.file_name or "downloaded_file"
    file_size = media.file_size
    chunk_size = 1024 * 1024  # 1 MiB
    total_chunks = (file_size + chunk_size - 1) // chunk_size

    await message.reply(f"Downloading {file_name} ({file_size} bytes) in {total_chunks} chunks...")

    # Shared dictionary to store chunks
    chunk_storage = {}

    async def fetch_chunk(offset):
        """Fetch a specific chunk by its offset."""
        # Use the semaphore to limit concurrency
        async with semaphore:
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

    # List to hold all chunk download tasks
    tasks = []
    for offset in range(total_chunks):
        tasks.append(fetch_chunk(offset))

    # Process tasks in batches of 5 concurrently
    for i in range(0, len(tasks), 5):
        await asyncio.gather(*tasks[i:i+5])  # Process 5 tasks at a time

    # Write the chunks to the file in order
    with open(file_name, "wb") as file:
        for offset in range(total_chunks):
            if offset in chunk_storage:
                file.write(chunk_storage[offset])
            else:
                print(f"Warning: Missing chunk {offset + 1}")

    # After downloading the file, send it
    if media.video:
        await app.send_video(
            message.chat.id,
            file_name,
            caption="Here is your downloaded video!"
        )
    elif media.document:
        await app.send_document(
            message.chat.id,
            file_name,
            caption="Here is your downloaded document!"
        )
    elif media.audio:
        await app.send_document(
            message.chat.id,
            file_name,
            caption="Here is your downloaded audio!"
        )

    # Delete the file after sending it to free up space
    try:
        os.remove(file_name)
    except Exception as e:
        print(f"Error deleting file {file_name}: {e}")

    await message.reply(f"Download of {file_name} completed and sent!")

app.run()
