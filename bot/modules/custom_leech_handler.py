from pyrogram import filters
from pyrogram.handlers import MessageHandler
from ..helper.mirror_leech_utils.download_utils.direct_link_generator import direct_link_generator
from ..helper.telegram_helper.message_utils import delete_message, send_message, get_tg_link_message
from ..helper.telegram_helper.filters import CustomFilters
from ..helper.telegram_helper.bot_commands import BotCommands
from ..helper.ext_utils.bot_utils import get_content_type
from ..helper.ext_utils.links_utils import is_url
from .. import bot_loop
from .mirror_leech import Mirror
from ..core.mltb_client import TgClient
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configure your channel IDs here
SOURCE_CHANNEL = -1004898495389  # Replace with your source channel ID
DATA_STORE_CHANNEL = -1002464896968  # Replace with your data store channel ID 
DESTINATION_CHANNEL = -1002487065354  # Replace with your destination channel ID

class CustomLeechHandler:
    def __init__(self, client, message):
        self.client = client
        self.message = message
        
    async def handle_leech(self):
        """Handle the custom leech workflow"""
        msg_parts = self.message.text.split(" ", 1)
        if len(msg_parts) != 2:
            await send_message(self.message, "Please provide a URL with the leech command!")
            return

        url = msg_parts[1].strip()
        
        if not is_url(url):
            await send_message(self.message, "Please provide a valid URL!")
            return

        # Send status message
        status_msg = await send_message(
            self.message, 
            f"📥 Processing URL: {url}\n\nDownloading and uploading to Data Store Channel..."
        )

        try:
            # Set LEECH_DUMP_CHAT in config for data store channel
            from ..core.config_manager import Config
            original_leech_dump = Config.LEECH_DUMP_CHAT
            Config.LEECH_DUMP_CHAT = str(DATA_STORE_CHANNEL)

            # Create Mirror instance with leech=True to upload to Telegram
            mirror_handler = Mirror(
                self.client,
                self.message,
                is_leech=True
            )
            
            # Start the leech process
            await mirror_handler.new_event()
            
            # Wait for the file to be uploaded
            import asyncio
            await asyncio.sleep(5)  # Give some time for the upload to complete
            
            # Get the last message from data store channel
            messages = await self.client.get_messages(DATA_STORE_CHANNEL, limit=1)
            if not messages or len(messages) == 0:
                raise Exception("Failed to get uploaded file message")
                
            file_msg = messages[0]
            file_link = f"https://t.me/c/{str(DATA_STORE_CHANNEL)[4:]}/{file_msg.id}"
            
            # Restore original LEECH_DUMP_CHAT
            Config.LEECH_DUMP_CHAT = original_leech_dump

            # Create the final message for destination channel
            final_msg = f"🔗 Original URL: {url}\n📁 File Link: {file_link}"
            
            # Send to destination channel
            await self.client.send_message(
                DESTINATION_CHANNEL,
                final_msg,
                disable_web_page_preview=True
            )

            await delete_message(status_msg)
            await send_message(
                self.message,
                "✅ Successfully processed the URL and uploaded to channels!"
            )

        except Exception as e:
            await send_message(self.message, f"❌ Error: {str(e)}")
            await delete_message(status_msg)

def add_handler():
    """Add the custom leech handler to the bot"""
    TgClient.bot.add_handler(
        MessageHandler(
            handle_custom_leech,
            filters=filters.command(BotCommands.LeechCommand) & 
                    filters.chat(SOURCE_CHANNEL) &
                    CustomFilters.authorized
        )
    )

async def handle_custom_leech(client, message):
    """Entry point for the custom leech command"""
    handler = CustomLeechHandler(client, message)
    bot_loop.create_task(handler.handle_leech())
