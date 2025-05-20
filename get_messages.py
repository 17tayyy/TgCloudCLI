from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
import json

with open("config.json") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
chat_id = config["chat_id"]

client = TelegramClient("tgcloud", api_id, api_hash)

def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

async def getmsgs(client, chat_id):
    messagesid = []
    files = 0
    async for message in client.iter_messages(chat_id):
        file_name = None
        size = None
        mime_type = None

        if isinstance(message.media, MessageMediaDocument) and message.media.document:
            doc = message.media.document
            for attr in doc.attributes:
                if hasattr(attr, 'file_name'):
                    file_name = attr.file_name
                    break
            size = doc.size
            mime_type = doc.mime_type

        elif isinstance(message.media, MessageMediaPhoto) and message.media.photo:
            file_name = "photo.jpg"
            size = None
            mime_type = "image/jpeg"

        if file_name:
            files += 1
            size_str = human_readable_size(size) if size is not None else "Unknown"
            print(f"""[+] File found
    ID: {message.id}
    Name: {file_name}
    Size: {size_str}
    MIME: {mime_type}
    Date: {message.date}
    Text: {message.text}
    """)
        messagesid.append(message.id)
    print(f"[+] Total files found: {files}")
    return messagesid

with client:
     messages = client.loop.run_until_complete(getmsgs(client, chat_id)) 