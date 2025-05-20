# TgCloud V2 ☁️🚀

**TgCloud V2** is a console-based cloud storage system that uses Telegram as a secure backend. Upload, download, organize, and manage large files directly from your terminal, with optional encryption for extra privacy.

---

## Features

- 📁 **Virtual folders:** Organize your files in a folder-like structure.
- 🔒 **Optional encryption:** Encrypt files before uploading and decrypt after downloading with a local key.
- 📤 **Progress bars:** See real-time, colored progress bars for uploads and downloads.
- 🗑️ **Remote deletion:** Delete files from Telegram and your local structure.
- 📝 **Large file support:** Works with files up to 2GB (regular accounts) or 4GB (Telegram Premium).
- 🐧 **User-friendly CLI:** Simple commands and built-in help.
- 🎨 **Colorful interface:** Clear, colored feedback for a better experience.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/youruser/TgCloudV2.git
   cd TgCloudV2
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your Telegram credentials:**
   - Create `config.json` with your `api_id`, `api_hash`, and `chat_id`.

---

## Quick Start

1. **Run the system:**
   ```bash
   python3 TgCloud.py
   ```

2. **Main commands:**

   | Command            | Description                                 |
   |--------------------|---------------------------------------------|
   | `ls`               | List files or folders                       |
   | `cd <folder>`      | Enter a folder                              |
   | `cd ..`            | Return to root                              |
   | `mkdir <name>`     | Create a new folder                         |
   | `put <file>`       | Upload a file                               |
   | `get <file>`       | Download a file                             |
   | `rm <file>`        | Delete a file                               |
   | `encryption`       | Toggle encryption/decryption mode           |
   | `help`             | Show help                                   |
   | `exit`             | Exit the system                             |

3. **Encryption:**
   - Type `encryption` to toggle encryption mode ON/OFF.
   - When enabled, files are encrypted before upload and decrypted after download.
   - The encryption key is stored locally as `encryption.key`.

---

## Example Usage

```shell
TgCloud/ > mkdir backups
TgCloud/ > cd backups
TgCloud/backups > encryption
[+] Encryption enabled
TgCloud/backups > put secret.zip
[+] Encrypting file before upload...
[+] Uploading secret.zip [#######---------] 60%
...
[+] Uploaded 'secret.zip'
TgCloud/backups > get secret.zip
[+] Downloading secret.zip [##########-----] 80%
[+] Decrypting file after download...
[+] Downloaded: secret.zip
```

---

## Requirements

- Python 3.8+
- [Telethon](https://github.com/LonamiWebs/Telethon)
- [cryptography](https://cryptography.io/)
- [tqdm](https://tqdm.github.io/)
- [termcolor](https://pypi.org/project/termcolor/)

Install all dependencies with:
```bash
pip install -r requirements.txt
```

---

## Credits

Developed by [your name or alias].  
Inspired by the flexibility and privacy of Telegram.

---

## License

MIT License

---