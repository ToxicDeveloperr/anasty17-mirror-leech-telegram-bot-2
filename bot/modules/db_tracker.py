"""Simple task tracking without database"""

from typing import Dict, Optional

# Simple in-memory storage
tasks: Dict[str, dict] = {}
gid_task_mapping: Dict[str, str] = {}

async def add_task(task_id: str, url: str, gid: Optional[str] = None) -> None:
    """Add a task to tracking"""
    tasks[task_id] = {"url": url, "status": "pending", "gid": gid}
    if gid:
        gid_task_mapping[gid] = task_id

async def update_task_status(task_id: str, status: str, file_message_id: int = None) -> None:
    """Update task status"""
    if task_id in tasks:
        tasks[task_id].update({
            "status": status,
            "message_id": file_message_id
        })

async def get_task(task_id: str) -> Optional[dict]:
    """Get task info"""
    return tasks.get(task_id)

async def get_task_by_gid(gid: str) -> Optional[dict]:
    """Get task by GID"""
    task_id = gid_task_mapping.get(gid)
    if task_id:
        return tasks.get(task_id)
    return None

async def delete_task(task_id: str) -> None:
    """Delete task from tracking"""
    if task_id in tasks:
        if gid := tasks[task_id].get("gid"):
            gid_task_mapping.pop(gid, None)
        del tasks[task_id]
