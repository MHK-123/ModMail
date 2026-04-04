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
SHIP_RENDER_URL        =    # URL of your Render rendering service (required for -ship)
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

## 🛠️ Deployment Architecture (Hybrid)

This bot uses a **Hybrid Cloud Architecture** for maximum performance and premium features:
1. **GitHub Actions**: Run the bot logic (ModMail, events, roles).
2. **Render.com**: Hosts the Image Rendering Microservice (Playwright + FastAPI).

---

## 🌎 Step 1: Deploy Render Service

1. Log in to [Render.com](https://dashboard.render.com).
2. Click **New** > **Web Service**.
3. Point it to the `render-service/` folder in this repository.
4. Set **Runtime** to `Docker` (using the provided `Dockerfile`).
5. Once live, copy the **Service URL**.

---

## 🤖 Step 2: Creating & Setting the Discord Bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** → give it a name
3. Go to **Bot** tab → click **Add Bot**
4. Copy the **Bot Token** — you'll need this for environment variables.
5. Under **Privileged Gateway Intents**, enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent

---

## 🔑 Step 3: Environment Configuration

### GitHub Actions (Production)
If you are running the bot on GitHub Actions, add these to your **Repository Secrets**:
- `DISCORD_TOKEN`: Your bot token.
- `SHIP_RENDER_URL`: Your Render service URL.

### Local Development (.env)
Create a file named `.env` in the same folder as `main.py`:

```
DISCORD_TOKEN=your_bot_token_here
SHIP_RENDER_URL=your_render_url_here
```

---

## ▶️ Running & Verification

**Requirements:** Python 3.10+

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

The bot will log in and sync slash commands automatically. Verified Render images will be fetched via HTTP during the `-ship` command.

---

## 📦 Files to Deliver (When Selling)

Send the buyer these files:

```
ModMail/
├── main.py              ← Core bot logic
├── render-service/      ← Image rendering microservice
├── requirements.txt     ← Dependencies
├── README.md            ← Feature reference
└── GUIDE.md             ← This file
```

**Do NOT include:**
- `.env`
- `modmail_data.json`
