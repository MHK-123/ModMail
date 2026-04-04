# DungeonKeeper ModMail Bot 🛡️

A professional Discord ModMail and Staff Management bot designed for high-volume moderation teams. Features a clean reporting UI, automated staff events, and a comprehensive premium membership system.

## 🌟 Key Features

### 📬 Advanced ModMail System
- **Thread-Based Support**: Each user report creates a dedicated thread in the staff channel.
- **Interactive UI**: Buttons for **Reply**, **Warn**, **Mute**, **Ban**, **Close**, and **Blacklist**.
- **Real-Time Forwarding**: DMs from users are instantly forwarded to threads, and staff replies are sent back to DMs.
- **Inactivity Timer**: Sessions automatically expire after 5 minutes of inactivity to keep reports fresh.

### ⚒️ Staff Management
- **Promotion/Demotion Logs**: Automatic branded embeds sent to staff members upon role changes.
- **Rule Tracking**: Staff guidelines are linked directly in promotion messages.
- **Role-Based Permissions**: Granular access control for owners, higher staff, and regular staff.

### 💎 Premium Membership System
Exclusive features for your most dedicated supporters:
- **Automated Onboarding**: Instant purchase confirmation and expiry notification DMs.
- **Custom Interactive Commands**:
  - `-kick @user`: Fun kick GIF interaction.
  - `-slap @user`: Random slap GIF.
  - `-hug @user`: Wholesome hug GIF.
  - `-kiss @user`: Sweet kiss GIF.
  - `-ship @user`: Dynamic compatibility match image generation using **Pillow**.

---

## 🚀 Quick Start

### 📋 Prerequisites
- **Python 3.10+**
- **Discord Bot Token** (Intents: `Members`, `Message Content` enabled)
- **Role IDs**: Configured in `main.py` (Owner, Higher, Staff, Premium).

### 🛠️ Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/MHK-123/ModMail.git
   cd ModMail
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (`.env`):
   ```env
   DISCORD_TOKEN=your_token_here
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

---

## 🤖 Premium Commands

| Command | Action | GIF/Image |
| :--- | :--- | :--- |
| `-hug @user` | Hugs a user | Wholesome cuddle GIFs |
| `-kick @user` | Kicks a user (fun) | High-kick anime/bear GIFs |
| `-slap @user` | Slaps a user | Funny cat/penguin slap GIFs |
| `-kiss @user` | Kisses a user | Romantic/cute kiss GIFs |
| `-punch @user`| Punches a user | Intense anime punch GIFs |
| `-ship @user` | Compatibility Match | 1000x320 Dynamic Image 💞 |

---

## 🛠️ Configuration

The following IDs must be updated in `main.py`:
- `GUILD_ID`: Your Discord Server ID.
- `REPORT_CHANNEL_ID`: Channel where ModMail threads are created.
- `LOG_CHANNEL_ID`: Channel for bot action logs.
- `PREMIUM_ROLE_ID`: ID of the role that unlocks premium commands.

---

## 📜 Credits & License
Developed for **DungeonKeeper**. Assets provided by **Klipy**.

