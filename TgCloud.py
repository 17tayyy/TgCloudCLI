import os
import sys
import json
import signal
import asyncio
import readline
from telethon import TelegramClient
from telethon.tl.functions.messages import DeleteMessagesRequest
from telethon.tl.types import DocumentAttributeFilename
from termcolor import colored
from tqdm import tqdm
from cryptography.fernet import Fernet

with open("config.json") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
chat_id = int(config["chat_id"])

client = TelegramClient("tgcloud", api_id, api_hash)
current_folder = None
structure = {}
encription = False

def def_handler(sig, frame):
    print(colored("\n\n[!]  Exiting TgCloud...", "red"))
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

def banner():
    print(colored(r"""
  _____      ____ _                 _ 
 |_   _|_ _ / ___| | ___  _   _  __| |
   | |/ _` | |   | |/ _ \| | | |/ _` |
   | | (_| | |___| | (_) | |_| | (_| |   [by tay] 
   |_|\__, |\____|_|\___/ \__,_|\__,_|      V2
      |___/                                                                                                                                              
    """, 'magenta'))

def load_structure():
    global structure
    os.makedirs("structures", exist_ok=True)
    if os.path.exists("structures/structure.json"):
        with open("structures/structure.json", "r") as f:
            structure = json.load(f)

def save_structure():
    with open("structures/structure.json", "w") as f:
        json.dump(structure, f, indent=4)

async def create_folder(name):
    if name in structure:
        print(colored("\n[!] Folder already exists", "red"))
        return
    structure[name] = []
    save_structure()
    print(colored(f"\n[+] Created folder '{name}'", "green"))

def encrypt_file(file_path):
    if not os.path.exists(file_path):
        print(colored("\n[!] File does not exist", "red"))
        return None

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
        return None

    key_path = "./encryption.key"
    if not os.path.exists(key_path):
        print(colored("\n[!] Encryption key not found. Cannot decrypt the file.", "red"))
        return None

    with open(key_path, "rb") as key_file:
        key = key_file.read()

    fernet = Fernet(key)

    with open(file_path, "rb") as file:
        encrypted_data = file.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        print(colored(f"\n[!] Failed to decrypt the file: {e}", "red"))
        return None

    with open(file_path, "wb") as file:
        file.write(decrypted_data)
    return file_path

async def download_file(name):
    global encription
    if current_folder is None:
        print(colored("\n[!] No folder selected", "red"))
        return

    file_info = next((f for f in structure[current_folder] if f["filename"] == name), None)
    if not file_info:
        print(colored("\n[!] File not found", "red"))
        return

    message = await client.get_messages(chat_id, ids=file_info["message_id"])
    size = None
    desc_text = colored(f"[+] Downloading {file_info['filename']}", 'blue')
    if message.document:
        size = message.document.size
    elif message.media and hasattr(message.media, "document") and message.media.document:
        size = message.media.document.size

    print()
    progress = tqdm(total=size, unit='B', unit_scale=True, desc=desc_text, colour="magenta") if size else None

    def progress_callback(current, total):
        if progress:
            progress.n = current
            progress.refresh()

    path = await message.download_media(progress_callback=progress_callback)
    if progress:
        progress.close()
    print(colored(f"\n[+] Downloaded: {path}", "green"))

    if encription and path:
        print(colored("\n[+] Decrypting file after download...", 'yellow'))
        decrypted_path = decrypt_file(path)
        if decrypted_path:
            print(colored(f"\n[+] Decrypted: {decrypted_path}", 'green'))
        else:
            print(colored("\n[!] Decryption failed.", 'red'))

async def upload_file(path):
    global encription
    if current_folder is None:
        print(colored("\n[!] No folder selected. Use 'cd <folder>'", "red"))
        return

    upload_path = path
    if encription:
        print(colored("\n[+] Encripting file before upload...", 'yellow'))
        upload_path = encrypt_file(path)
        if not upload_path:
            print(colored("[!] Encryption failed.", 'red'))
            return
        
    file_size = os.path.getsize(upload_path)
    desc_text = colored(f"[+] Uploading {os.path.basename(path)}", 'blue')
    print()
    progress = tqdm(total=file_size, unit='B', unit_scale=True, desc=desc_text, colour="magenta")

    def progress_callback(current, total):
        progress.n = current
        progress.refresh()

    message = await client.send_file(
        chat_id,
        file=upload_path,
        caption=os.path.basename(path),
        attributes=[DocumentAttributeFilename(os.path.basename(path))],
        progress_callback=progress_callback
    )
    progress.close()

    structure[current_folder].append({
        "filename": os.path.basename(path),
        "message_id": message.id
    })
    save_structure()
    print(colored(f"\n[+] Uploaded '{path}'", "yellow"))

    if encription and upload_path != path:
        os.remove(upload_path)

def list_files():
    if current_folder is None:
        print()
        for folder in structure:
            print(colored(f" - {folder}", "blue"))
    else:
        print()
        for f in structure[current_folder]:
            print(colored(f" {f['filename']}", "green"))

def change_directory(folder):
    global current_folder
    if folder not in structure:
        print(colored("\n[!] Folder not found", "red"))
        return
    current_folder = folder
    print(colored(f"\n[+] Entered folder '{folder}'", "cyan"))

async def delete_file(name):
    if current_folder is None:
        print(colored("\n[!] No folder selected", "red"))
        return
    entry = next((f for f in structure[current_folder] if f["filename"] == name), None)
    if not entry:
        print(colored("\n[!] File not found", "red"))
        return
    await client.delete_messages(chat_id, entry["message_id"])
    structure[current_folder].remove(entry)
    save_structure()
    print(colored(f"\n[+] Deleted '{name}'", "yellow"))

def remove_directory(dir):
    global current_folder
    if dir not in structure:
        print(colored("\n[!] Folder not found", 'red'))
        return
    if current_folder == dir:
        print(colored("\n[!] Can't remove your current directory", 'red'))
        return
    del structure[dir]
    save_structure()
    print(colored(f"\n[+] Deleted '{dir}' dir", 'green'))

async def pseudo_shell():
    global current_folder, encription
    banner()
    print(colored("[+] Type 'help' for commands", "blue"))
    while True:
        cmd = input(colored(f"\nTgCloud/{current_folder or ''} > ", "magenta")).strip()
        if cmd == "exit":
            print(colored("\n[!] Exiting TgCloud...", "red"))
            break
        elif cmd == "help":
            print(colored(help_menu(), "blue"))
        elif cmd == "ls":
            list_files()
        elif cmd == "cd ..":
            current_folder = None
        elif cmd == "encryption":
            if encription:
                print(colored("\n[+] Encription disabled", 'red'))
                encription = False
            else:
                print(colored("\n[+] Encription enabled", 'green'))
                encription = True
        elif cmd.startswith("cd "):
            change_directory(cmd.split(" ", 1)[1])
        elif cmd.startswith("mkdir "):
            await create_folder(cmd.split(" ", 1)[1])
        elif cmd.startswith("rmdir"):
            remove_directory(cmd.split(" ", 1)[1])
        elif cmd.startswith("put "):
            await upload_file(cmd.split(" ", 1)[1])
        elif cmd.startswith("get "):
            await download_file(cmd.split(" ", 1)[1])
        elif cmd.startswith("rm "):
            await delete_file(cmd.split(" ", 1)[1])
        else:
            print(colored("\n[!] Unknown command", "red"))

def help_menu():
    return """
    Commands:
    ---------
    ls                 - List files or folders
    mkdir <name>       - Create folder (virtual)
    cd <name>          - Enter folder
    cd ..              - Return to root
    put <file>         - Upload file
    get <file>         - Download file
    rm <file>          - Delete file
    encryption         - Turns on/off the encryption/decryption of files
    exit               - Exit
    """

async def main():
    await client.start()
    load_structure()
    await pseudo_shell()

if __name__ == "__main__":
    asyncio.run(main())
