from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URL = "mongodb+srv://tejaschavan1110:cSxC44OLfIPxcXxp@cluster0.iu0f4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client['leech_tracker']
tasks_collection = db['leech_tasks']

async def add_task(task_id, url):
    """Add task to MongoDB"""
    tasks_collection.insert_one({
        'task_id': task_id,
        'source_url': url,
        'status': 'downloading',
        'created_at': datetime.now(),
        'file_message_id': None
    })

async def update_task_status(task_id, status, file_message_id=None):
    """Update task status in MongoDB"""
    update_data = {'status': status}
    if file_message_id:
        update_data['file_message_id'] = file_message_id
    tasks_collection.update_one(
        {'task_id': task_id},
        {'$set': update_data}
    )

async def get_task(task_id):
    """Get task from MongoDB"""
    return tasks_collection.find_one({'task_id': task_id})

async def delete_task(task_id):
    """Delete task from MongoDB"""
    tasks_collection.delete_one({'task_id': task_id})
