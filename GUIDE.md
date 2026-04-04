# DungeonKeeper Bot — Setup & Deployment Guide

This guide covers everything needed to configure, deploy, and sell/hand off this bot.

---

## 🔧 What to Change (Server Customisation)

Open `main.py` and update the following constants at the top of the file:

```python
# ── IDs ─────────────────────────────────────────────────────────────────────
GUILD_ID               =    # Your Discord Server ID
REPORT_CHANNEL_ID      =    # Channel where ModMail threads are created
LOG_CHANNEL_ID         =    # Channel where all actions are logged
MODERATION_CHANNEL_ID  =    # Moderation / staff channel
ANNOUNCEMENT_CHANNEL_ID =   # Announcements channel

OWNER_ROLE_ID          =    # Owner role ID
HIGHER_ROLE_ID         =    # Higher staff role ID
STAFF_ROLE_ID          =    # Base staff role ID
PREMIUM_ROLE_ID        =    # Premium role ID
```

### Rules Channel

The bot sends a clickable channel mention when staff use `/rules`. Update the channel ID in the `/rules` command in `main.py`:

```python
await user.send(f"...please review the rules here: <#1318959296884768798>")
```

### How to get the IDs

1. Enable **Developer Mode** in Discord: Settings → Advanced → Developer Mode ✅
2. Right-click any server, channel, or role → **Copy ID**

---

## 🤖 Creating the Discord Bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** → give it a name
3. Go to **Bot** tab → click **Add Bot**
4. Copy the **Bot Token** — you'll need this for `.env`
5. Under **Privileged Gateway Intents**, enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Send Messages in Threads`, `Create Public Threads`, `Embed Links`, `Manage Threads`, `Read Message History`, `Mention Everyone`, `Add Reactions`

---

## 🔑 Environment File

Create a file named `.env` in the same folder as `main.py`:

```
DISCORD_TOKEN=your_bot_token_here
```

> ⚠️ Never share or commit your `.env` file. Add it to `.gitignore`.

---

## ▶️ Running Locally

**Requirements:** Python 3.10+

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

The bot will log in and sync slash commands automatically.

---

## ☁️ Free Hosting

### Option 1 — Railway (Recommended)
1. Push your code to a private GitHub repo.
2. Connect it to Railway.
3. Add `DISCORD_TOKEN` in the **Variables** tab.

---

## 📦 Files to Deliver (When Selling)

Send the buyer these files:

```
ModMail/
├── main.py              ← Core bot 
├── requirements.txt     ← Dependencies
├── README.md            ← Feature reference
└── GUIDE.md             ← This file
```

**Do NOT include:**
- `.env`
- `modmail_data.json`
