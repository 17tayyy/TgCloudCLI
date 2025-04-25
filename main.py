import telebot 
import os
from dotenv import load_dotenv
import sys
import threading
import readline
from tqdm import tqdm
import time
from cryptography.fernet import Fernet
import json
import signal
from termcolor import colored

load_dotenv()

BOT_TOKEN =  os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
structure = {}
topic_ids = {}
current_folder = None
current_topic_id = None
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
telebot.apihelper.CONNECT_TIMEOUT = 60
telebot.apihelper.READ_TIMEOUT = 60

def def_handler(sig, frame):
    print(colored("\n\n[!]  Exiting TgCloud...", "red"))
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

def banner():
    print(colored(fr"""
  _____      ____ _                 _ 
 |_   _|_ _ / ___| | ___  _   _  __| |
   | |/ _` | |   | |/ _ \| | | |/ _` |
   | | (_| | |___| | (_) | |_| | (_| |   [by tay] 
   |_|\__, |\____|_|\___/ \__,_|\__,_|
      |___/                                                                                                                                              """, 'magenta'))

def pseudo_shell():
    global current_folder
    print(colored(f"\n[+] Connection established with Telegram", "magenta"))
    print(colored(f"[+] Connected to chat: {CHAT_ID}", "magenta"))
    print(colored("\n[+] Type 'help' for a list of commands", "blue"))
    print(colored("[+] Type 'exit' to exit the shell", "blue"))
    while True:
        command = None
        if current_folder is not None:
            command = input(colored(f"\nTgCloud/{colored(current_folder, 'blue')}{colored("/ > ", 'magenta')}", "magenta"))
        else:
            command = input(colored("\nTgCloud > ", "magenta"))
        if command == "exit":
            print(colored("\n[!]  Exiting TgCloud...", "red"))
            break
        elif command == "help":
            print(colored(help_menu(), "blue"))
        elif command == "clear":
            os.system("cls" if os.name == "nt" else "clear")
        elif command == "cd ..":
            if current_folder is not None:
                current_folder = None
            else:
                print(colored("\n[!] Already in root directory", "red"))
        elif command.startswith("cd"):
            folder_name = command.split(" ")[1]
            change_directory(folder_name)
        elif command.startswith("rmdir"):
            folder_name = command.split(" ")[1]
            remove_folder(folder_name)
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
            print(colored("\n[!]  Invalid command", "red"))

def help_menu():
    return """
    TgCloud Help Menu:
    ------------------
    cd <folder_name>     - Change directory to a folder
    mkdir <folder_name>  - Create a new folder
    put <file_path>      - Upload a file
    get <file_name>      - Download a file
    rm <file_name>       - Delete a file
    rmdir <folder_name>  - Remove a folder
    ls                   - List all files in the current folder
    help                 - Show this menu
    exit                 - Exit TgCloud"""

def set_encryption_key():
    key_path = "./encryption.key"
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)

def encrypt_file(file_path):
    if not os.path.exists(file_path):
        print(colored("\n[!] File does not exist", "red"))
        return

    key_path = "./encryption.key"
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
    else:
        with open(key_path, "rb") as key_file:
            key = key_file.read()

    fernet = Fernet(key)

    with open(file_path, "rb") as file:
        original_data = file.read()

    encrypted_data = fernet.encrypt(original_data)

    encrypted_file_path = f"encrypted_{os.path.basename(file_path)}"
    with open(encrypted_file_path, "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)

    return encrypted_file_path

def decrypt_file(file_path):
    if not os.path.exists(file_path):
        print(colored("\n[!] File does not exist", "red"))
        return

    key_path = "./encryption.key"
    if not os.path.exists(key_path):
        print(colored("\n[!] Encryption key not found. Cannot decrypt the file.", "red"))
        return

    with open(key_path, "rb") as key_file:
        key = key_file.read()

    fernet = Fernet(key)

    with open(file_path, "rb") as file:
        encrypted_data = file.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        print(colored(f"\n[!] Failed to decrypt the file: {e}", "red"))
        return

    with open(file_path, "wb") as file:
        file.write(decrypted_data)

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
        print(colored("\n[!] Folder already exists", "red"))
        return
    topic = bot.create_forum_topic(CHAT_ID, name=folder_name)
    structure[folder_name] = []
    topic_ids[folder_name] = topic.message_thread_id
    save_structure()

def remove_folder(folder_name):
    if folder_name not in structure:
        print(colored("\n[!] Folder does not exist", "red"))
        return

    sure = input(colored(f"\n[!] Are you sure you want to delete the folder {folder_name}? (y/n): ", "red"))
    if sure.lower() != "y":
        print(colored("\n[!]  Operation cancelled", "red"))
        return

    bot.delete_forum_topic(CHAT_ID, topic_ids[folder_name])
    del structure[folder_name]
    del topic_ids[folder_name]
    save_structure()
    print(colored(f"\n[+] Removed folder {folder_name}", "green"))

def upload_file(file_path):
    if current_folder is None:
        print(colored("\n[!] No folder selected. Use 'cd <folder>' first.", "red"))
        return

    if not os.path.exists(file_path):
        print(colored("\n[!] File does not exist", "red"))
        return

    file_name = os.path.basename(file_path)

    stop_progress = False

    def progress_animation():
        print()
        with tqdm(desc=f"{colored("[+] Uploading", 'blue')}", ncols=80, ascii=True) as progress:
            while not stop_progress:
                progress.update(1)
                time.sleep(0.1)

    progress_thread = threading.Thread(target=progress_animation)
    progress_thread.start()

    encrypted_file_path = encrypt_file(file_path)
    file_name = os.path.basename(file_path)

    try:
        with open(encrypted_file_path, "rb") as f:
            msg = bot.send_document(
                CHAT_ID,
                f,
                caption=file_path,
                message_thread_id=topic_ids[current_folder]
            )
    finally:
        stop_progress = True 
        progress_thread.join()
        os.remove(encrypted_file_path)

    structure[current_folder].append({
        "filename": file_name,
        "file_id": msg.document.file_id,
        "message_id": msg.message_id,
        "file_size": msg.document.file_size,
        "file_type": msg.document.mime_type
    })

    save_structure()
    print(colored(f"\n[+] Uploaded {file_name} to {current_folder}", "green"))

def download_file(file_name):
    if current_folder is None:
        print(colored("\n[!] No folder selected. Use 'cd <folder>' first.", "red"))
        return

    files = structure.get(current_folder, [])
    file = next((a for a in files if a["filename"] == file_name), None)

    if not file:
        print(colored("\n[!] File not found", "red"))
        return
    
    file_id = file["file_id"]
    file_name = file["filename"]
    file_path = os.path.join(os.getcwd(), file_name)
    stop_progress = False

    def progress_animation():
        print()
        with tqdm(desc=f"{colored("[+] Downloading", 'blue')}", ncols=80, ascii=True) as progress:
            while not stop_progress:
                progress.update(1)
                time.sleep(0.1)
    progress_thread = threading.Thread(target=progress_animation)
    progress_thread.start()
    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, "wb") as f:
            f.write(downloaded_file)
    finally:
        stop_progress = True 
        progress_thread.join()
    decrypt_file(file_path)
    print(colored(f"\n[+] Downloaded {file_name}", "green"))

def delete_file(file_name):
    if current_folder is None:
        print(colored("\n[!] No folder selected. Use 'cd <folder>' first.", "red"))
        return

    files = structure.get(current_folder, [])
    file = next((a for a in files if a["filename"] == file_name), None)

    if not file:
        print(colored("\n[!] File not found", "red"))
        return

    try:
        bot.delete_message(CHAT_ID, file["message_id"])
    except Exception as e:
        print(colored(f"\n[!] Failed to delete message: {e}", "red"))

    structure[current_folder] = [a for a in files if a["filename"] != file_name]
    save_structure()

def change_directory(folder_name):
    global current_folder, current_topic_id
    if folder_name not in structure:
        print(colored("\n[!] Folder does not exist", "red"))
        return
    current_folder = folder_name
    current_topic_id = topic_ids[folder_name]

def list_files():
    if current_folder is None:
        print()
        for folder in structure.keys():
            print(colored(f" - {folder}", "blue"))
        return

    files = structure.get(current_folder, [])
    if not files:
        return
    
    print()
    for file in files:
        print(colored(f" {file['filename']} - ({file['file_size']}B) - {file['file_type']}", "green"))

if __name__ == '__main__':
    if not BOT_TOKEN or not CHAT_ID:
        print(colored("\n[!]  Please set the BOT_TOKEN and CHAT_ID in the .env file", "red"))
        sys.exit(1)

    if not os.path.exists("./encryption.key"):
        set_encryption_key()

    load_structure()
    banner()
    bot_thread = threading.Thread(target=bot.polling, daemon=True)
    bot_thread.start()
    pseudo_shell()
