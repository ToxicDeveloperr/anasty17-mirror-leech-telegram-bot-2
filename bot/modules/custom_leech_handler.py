
from asyncio import sleep
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from .. import bot_loop, LOGGER
from ..helper.telegram_helper.message_utils import delete_message, send_message
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.ext_utils.links_utils import is_url
from ..core.mltb_client import TgClient
from ..core.config_manager import Config
from .mirror_leech import Mirror

# Configure your channel IDs here (these are correct with -100 prefix)
SOURCE_CHANNEL = -1002176533426
DATA_STORE_CHANNEL = -1002464896968
DESTINATION_CHANNEL = -1002487065354

async def handle_channel_leech(client, message):
    """Handle leech commands from the source channel"""
    status_msg = None
    try:
        msg_parts = message.text.split(" ", 1)
        if len(msg_parts) != 2:
            await send_message(message, "Please provide a URL with the leech command!")
            return

        url = msg_parts[1].strip()
        
        if not is_url(url):
            await send_message(message, "Please provide a valid URL!")
            return

        # Send status message
        status_msg = await send_message(
            message, 
            f"📥 Processing URL: {url}\n\nDownloading and uploading to Data Store Channel..."
        )

        # Store original leech chat
        original_dump_chat = Config.LEECH_DUMP_CHAT
        Config.LEECH_DUMP_CHAT = str(DATA_STORE_CHANNEL)
            
        # Create mirror instance
        mirror = Mirror(
            client,
            message,
            is_leech=True,
        )
        
        # Start the leech process
        await mirror.new_event()
        
        # Wait for download and upload to complete
        from .. import task_dict, task_dict_lock
        async with task_dict_lock:
            task = task_dict.get(mirror.mid)
        
        if task:
            while task in task_dict:
                await sleep(2)
            
            # Wait briefly for the file to be processed
            await sleep(3)
            
            # Get most recent message from data store channel
            messages = await client.get_messages(DATA_STORE_CHANNEL, limit=1)
            if not messages or not messages[0]:
                raise Exception("Could not find uploaded file message")
                
            file_msg = messages[0]
            
            # Generate file link
            channel_id = str(DATA_STORE_CHANNEL)[4:] 
            file_link = f"https://t.me/c/{channel_id}/{file_msg.id}"

        # Create the final message
        final_msg = f"🔗 Original URL: {url}\n📁 File Link: {file_link}"
        
        # Send to destination channel
        await client.send_message(
            DESTINATION_CHANNEL,
            final_msg,
            disable_web_page_preview=True
        )

        # Clean up
        if status_msg:
            await delete_message(status_msg)
        await send_message(
            message,
            "✅ Successfully processed the URL and uploaded to channels!"
        )

    except Exception as e:
        LOGGER.error(str(e))
        await send_message(message, f"❌ Error: {str(e)}")
        if status_msg:
            await delete_message(status_msg)
    
    finally:
        # Restore original leech chat
        Config.LEECH_DUMP_CHAT = original_dump_chat

def add_handler():
    """Add the custom leech handler to the bot"""
    TgClient.bot.add_handler(
        MessageHandler(
            handle_channel_leech,
            filters=filters.command(BotCommands.LeechCommand) & 
                    filters.chat(SOURCE_CHANNEL) &
                    CustomFilters.authorized
        )
    )
