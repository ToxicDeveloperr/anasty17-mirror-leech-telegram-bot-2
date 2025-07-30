"""Simple task tracking without database"""

# Simple in-memory storage
tasks = {}

async def add_task(task_id: str, url: str) -> None:
    """Add a task to tracking"""
    tasks[task_id] = {"url": url, "status": "pending"}

async def update_task_status(task_id: str, status: str, file_message_id: int = None) -> None:
    """Update task status"""
    if task_id in tasks:
        tasks[task_id].update({
            "status": status,
            "message_id": file_message_id
        })

async def get_task(task_id: str) -> dict:
    """Get task info"""
    return tasks.get(task_id)

async def delete_task(task_id: str) -> None:
    """Delete task from tracking"""
    if task_id in tasks:
        del tasks[task_id]
