from ..ext_utils.db_tracker import update_task_status

class CustomTelegramUploader:
    @staticmethod
    async def on_upload_complete(task_id, message_id):
        """Update task status when upload completes"""
        await update_task_status(task_id, 'uploaded', message_id)
