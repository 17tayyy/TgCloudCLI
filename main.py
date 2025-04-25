import telebot 
import os
from dotenv import load_dotenv
import sys
import readline
import time
import json
import signal
load_dotenv()

BOT_TOKEN =  os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
structure = {}
topic_ids = {}
current_folder = None
current_topic_id = None
bot = telebot.TeleBot(BOT_TOKEN)

def def_handler(sig, frame):
    print("\n\n\n[!]  Exiting TgCloud...")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

def pseudo_shell():
    print("\n[+] Connection established with Telegram")
    print("[+] Type 'help' for a list of commands")
    print("[+] Type 'exit' to exit the shell")
    while True:
        command = input("\nTgCloud > ")
        if command == "exit":
            print("[!]  Exiting TgCloud...")
            break
        elif command == "help":
            print(help_menu())
        elif command.startswith("cd"):
            folder_name = command.split(" ")[1]
            change_directory(folder_name)
        elif command.startswith("mkdir"):
            folder_name = command.split(" ")[1]
            create_folder(folder_name)
        elif command.startswith("put"):
            file_path = command.split(" ")[1]
            upload_file(file_path)
        elif command.startswith("get"):
            file_name = command.split(" ")[1]
            download_file(file_name)
        elif command.startswith("rm"):
            file_name = command.split(" ")[1]
            delete_file(file_name)
        elif command == "ls":
            list_files()
        else:
            print("\n[!]  Invalid command")

def help_menu():
    return """
    TgCloud Help Menu:
    ------------------
    cd <folder_name>     - Change directory to a folder
    mkdir <folder_name>  - Create a new folder
    put <file_path>      - Upload a file
    get <file_name>      - Download a file
    rm <file_name>       - Delete a file
    ls                   - List all files in the current folder
    help                 - Show this menu
    exit                 - Exit TgCloud"""

def load_structure():
    global structure, topic_ids

    if not os.path.exists("./structures"):
        os.makedirs("./structures")

    if os.path.exists("./structures/structure.json"):
        with open("./structures/structure.json", "r") as f:
            structure = json.load(f)
    else:
        structure = {}

    if os.path.exists("./structures/topics.json"):
        with open("./structures/topics.json", "r") as f:
            topic_ids = json.load(f)
    else:
        topic_ids = {}

def save_structure():
    with open("./structures/structure.json", "w") as f:
        json.dump(structure, f, indent=4)

    with open("./structures/topics.json", "w") as f:
        json.dump(topic_ids, f, indent=4)

def create_folder(folder_name):
    if folder_name in structure:
        print("\n[!] Folder already exists")
        return
    topic = bot.create_forum_topic(CHAT_ID, name=folder_name)
    structure[folder_name] = []
    topic_ids[folder_name] = topic.message_thread_id
    save_structure()
    print(f"\n[+] Created folder {folder_name}")


def upload_file(file_path):
    if current_folder is None:
        print("\n[!] No folder selected. Use 'cd <folder>' first.")
        return

    if not os.path.exists(file_path):
        print("\n[!] File does not exist")
        return

    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        msg = bot.send_document(
            CHAT_ID,
            f,
            caption=file_name,
            message_thread_id=topic_ids[current_folder]
        )

    structure[current_folder].append({
        "filename": file_name,
        "file_id": msg.document.file_id,
        "message_id": msg.message_id
    })

    save_structure()
    print(f"\n[+] Uploaded {file_name} to {current_folder}")

def download_file(file_name):
    if current_folder is None:
        print("\n[!] No folder selected. Use 'cd <folder>' first.")
        return

    archivos = structure.get(current_folder, [])
    archivo = next((a for a in archivos if a["filename"] == file_name), None)

    if not archivo:
        print("\n[!] File not found")
        return

    try:
        file_info = bot.get_file(archivo["file_id"])
        downloaded = bot.download_file(file_info.file_path)

        with open(file_name, "wb") as f:
            f.write(downloaded)

        print(f"\n[+] Downloaded {file_name}")
    except Exception as e:
        print(f"\n[!] Failed to download file: {e}")

def delete_file(file_name):
    if current_folder is None:
        print("\n[!] No folder selected. Use 'cd <folder>' first.")
        return

    archivos = structure.get(current_folder, [])
    archivo = next((a for a in archivos if a["filename"] == file_name), None)

    if not archivo:
        print("\n[!] File not found")
        return

    try:
        bot.delete_message(CHAT_ID, archivo["message_id"])
    except Exception as e:
        print(f"\n[!] Failed to delete message: {e}")

    structure[current_folder] = [a for a in archivos if a["filename"] != file_name]
    save_structure()
    print(f"\n[+] Deleted {file_name} from {current_folder}")

def change_directory(folder_name):
    global current_folder, current_topic_id
    if folder_name not in structure:
        print("\n[!] Folder does not exist")
        return
    current_folder = folder_name
    current_topic_id = topic_ids[folder_name]
    print(f"\n[+] Changed directory to {folder_name}")

def list_files():
    if current_folder is None:
        print("\n[!] No folder selected. Use 'cd <folder>' first.")
        return

    archivos = structure.get(current_folder, [])
    if not archivos:
        print("\n[*] Folder is empty")
        return

    print(f"\n[*] Files in '{current_folder}':\n")
    for file in archivos:
        print(f" - {file['filename']}")

import threading

if __name__ == '__main__':
    print("[+] Starting TgCloud...")
    time.sleep(0.3)

    load_structure()

    bot_thread = threading.Thread(target=bot.polling, daemon=True)
    bot_thread.start()

    print("[+] TgCloud started")
    time.sleep(0.3)
    print("[+] Connecting to Telegram...")
    time.sleep(0.3)
    pseudo_shell()
