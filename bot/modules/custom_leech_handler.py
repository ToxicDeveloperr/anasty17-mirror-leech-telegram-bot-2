from asyncio import sleep
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from .. import bot_loop, LOGGER, task_dict, task_dict_lock
from ..helper.telegram_helper.message_utils import delete_message, send_message
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.ext_utils.links_utils import is_url
from ..core.mltb_client import TgClient
from ..core.config_manager import Config
from .mirror_leech import Mirror

# Channel IDs
SOURCE_CHANNEL = -1002176533426
DATA_STORE_CHANNEL = -1002464896968
DESTINATION_CHANNEL = -1002487065354

async def handle_multi_leech(client, message: Message):
    status_msg = None
    original_dump_chat = Config.LEECH_DUMP_CHAT

    try:
        # Extract all URLs
        urls = message.text.split()[1:]
        if not urls:
            await send_message(message, "Please provide at least one URL after /leech command!")
            return

        valid_urls = [url.strip() for url in urls if is_url(url.strip())]
        if not valid_urls:
            await send_message(message, "None of the provided inputs are valid URLs!")
            return

        status_msg = await send_message(message, f"📥 Processing {len(valid_urls)} URLs...")

        # Store uploaded file links
        uploaded_links = []

        for url in valid_urls:
            # Update Config
            Config.LEECH_DUMP_CHAT = str(DATA_STORE_CHANNEL)

            # Create mirror handler
            mirror = Mirror(client, message, is_leech=True, custom_url=url)
            await mirror.new_event()

            # Wait for completion
            async with task_dict_lock:
                task = task_dict.get(mirror.mid)

            if task:
                while task in task_dict:
                    await sleep(2)

            # Get last uploaded message from data store
            last_msgs = await client.get_messages(DATA_STORE_CHANNEL, limit=1)
            last_msg = last_msgs[0] if last_msgs else None
            if not last_msg:
                raise Exception(f"Upload failed for: {url}")

            link = f"https://t.me/c/{str(DATA_STORE_CHANNEL)[4:]}/{last_msg.id}"
            uploaded_links.append((url, link))

        # Final message
        final_msg = "\n\n".join([f"🔗 Original: {u}\n📁 File: {l}" for u, l in uploaded_links])

        await client.send_message(DESTINATION_CHANNEL, final_msg, disable_web_page_preview=True)

        if status_msg:
            await delete_message(status_msg)
        await send_message(message, "✅ All files processed and posted to destination!")

    except Exception as e:
        LOGGER.error(str(e))
        await send_message(message, f"❌ Error: {str(e)}")
        if status_msg:
            await delete_message(status_msg)

    finally:
        Config.LEECH_DUMP_CHAT = original_dump_chat


def add_handler():
    TgClient.bot.add_handler(
        MessageHandler(
            handle_multi_leech,
            filters=filters.command(BotCommands.LeechCommand) &
                    filters.chat(SOURCE_CHANNEL) &
                    CustomFilters.authorized
        )
    )
