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
```

### Rules Channel

The bot sends a clickable channel mention when staff use `/rules`. Update the channel ID in the `/rules` command in `main.py`:

```python
await user.send(f"...please review the rules here: <#YOUR_RULES_CHANNEL_ID>")
```

Replace `YOUR_RULES_CHANNEL_ID` with your actual rules channel ID.

### How to get the IDs

1. Enable **Developer Mode** in Discord: Settings → Advanced → Developer Mode ✅
2. Right-click any server, channel, or role → **Copy ID**

### Branding

Search for `DungeonKeeper` in `main.py` and replace it with your server name.
The embed footers say `"DungeonKeeper Moderation Team"` — update those too.

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
7. Copy the generated URL and open it to invite the bot to your server

---

## 🔑 Environment File

Create a file named `.env` in the same folder as `main.py`:

```
DISCORD_TOKEN=your_bot_token_here
```

> ⚠️ Never share or commit your `.env` file. Add it to `.gitignore`.

---

## ▶️ Running Locally

**Requirements:** Python 3.12+

```bash
# Install dependencies
pip install discord.py python-dotenv

# Run the bot
python main.py
```

The bot will log in and sync slash commands automatically.

---

## ☁️ Free Hosting

### Option 1 — Railway (Recommended Free Tier)

1. Sign up at [railway.app](https://railway.app)
2. Click **New Project → Deploy from GitHub repo** (push your code to a private GitHub repo first)
3. Add environment variable: `DISCORD_TOKEN` = your token
4. Railway auto-detects Python. Add a `Procfile`:
   ```
   worker: python main.py
   ```
5. Click **Deploy**

> Free tier gives 500 hours/month — enough for a single bot.

### Option 2 — Render

1. Sign up at [render.com](https://render.com)
2. Click **New → Background Worker**
3. Connect your GitHub repo
4. Set **Build Command:** `pip install -r requirements.txt`
5. Set **Start Command:** `python main.py`
6. Add environment variable: `DISCORD_TOKEN`
7. Click **Create Background Worker**

> Free tier spins down after inactivity — not ideal for bots but works.

---

## 💰 Paid Hosting (24/7 Reliable)

### Option 3 — Hostinger VPS (Recommended Paid)

1. Purchase a **KVM 1** plan at [hostinger.com](https://hostinger.com) (cheapest VPS, ~$5/month)
2. SSH into your server:
   ```bash
   ssh root@your_server_ip
   ```
3. Install Python:
   ```bash
   apt update && apt install python3 python3-pip -y
   ```
4. Upload your bot files (use FileZilla or `scp`):
   ```bash
   scp -r ./ModMail root@your_server_ip:/root/bot
   ```
5. Create `.env` on the server and paste your token
6. Install dependencies:
   ```bash
   pip3 install discord.py python-dotenv
   ```
7. Run persistently with `screen` or `pm2`:
   ```bash
   # Using screen (simple)
   screen -S bot
   python3 main.py
   # Press Ctrl+A then D to detach
   
   # Or using pm2 (recommended)
   npm install -g pm2
   pm2 start main.py --interpreter python3 --name "discord-bot"
   pm2 save
   pm2 startup
   ```

### Other Paid Options

| Provider | Starting Price | Notes |
|---|---|---|
| [DigitalOcean](https://digitalocean.com) | ~$4/month | Reliable, great docs |
| [Vultr](https://vultr.com) | ~$2.50/month | Cheapest VPS option |
| [Linode (Akamai)](https://linode.com) | ~$5/month | Very stable |

---

## 📦 Files to Deliver (When Selling)

Send the buyer these files:

```
ModMail/
├── main.py              ← Core bot (they edit this for their server)
├── requirements.txt     ← Dependencies
├── README.md            ← Feature reference
└── GUIDE.md             ← This file (setup instructions)
```

**Do NOT include:**
- `.env` (contains your token — never share)
- `modmail_data.json` (contains your server's session data)

---

## ✅ Quick Setup Checklist (For Buyers)

- [ ] Create a Discord bot at [discord.com/developers](https://discord.com/developers/applications)
- [ ] Enable **Server Members** and **Message Content** intents
- [ ] Copy bot token → create `.env` file
- [ ] Update all IDs and role IDs in `main.py`
- [ ] Replace `DungeonKeeper` with your server name throughout `main.py`
- [ ] Update `STAFF_RULES_LINK` to point to your rules message
- [ ] Invite bot to server with correct permissions
- [ ] Run `pip install discord.py python-dotenv`
- [ ] Run `python main.py`
- [ ] Verify slash commands appear in your server (may take a few seconds)
