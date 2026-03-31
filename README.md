# DungeonKeeper — Discord Bot

A fully-featured Discord moderation & community bot for the **DungeonKeeper** server.
Includes staff slash commands, automatic role onboarding DMs, and a complete ModMail support system.
All bot logic lives in a single file: `main.py`.

---

## Table of Contents

- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Required Bot Permissions](#required-bot-permissions)
- [Required Privileged Intents](#required-privileged-intents)
- [Slash Commands](#slash-commands)
- [ModMail System](#modmail-system)
- [Staff Buttons](#staff-buttons)
- [Automatic Behaviours](#automatic-behaviours)
- [Log System](#log-system)
- [Data Storage](#data-storage)
- [Channel & Role IDs](#channel--role-ids)
- [Deployment](#deployment)
- [File Structure](#file-structure)

---

## Setup

**Requirements**
- Python 3.12+
- pip packages: `discord.py`, `python-dotenv`

**Install dependencies**
```bash
pip install discord.py python-dotenv
```

**Run the bot**
```bash
python main.py
```

The bot syncs all slash commands to the guild instantly on startup (guild-scoped so changes appear immediately).

> For full deployment instructions (local, Railway, Render, Hostinger VPS) see **[GUIDE.md](GUIDE.md)**.

---

## Environment Variables

Create a `.env` file in the same folder as `main.py`:

```
DISCORD_TOKEN=your_bot_token_here
```

| Variable        | Description                                    |
|-----------------|------------------------------------------------|
| `DISCORD_TOKEN` | Your bot's token from Discord Developer Portal |

---

## Required Bot Permissions

Enable the following in your bot's OAuth2 invite URL and server permissions:

| Permission               | Reason                                      |
|--------------------------|---------------------------------------------|
| Send Messages            | Post embeds, replies, and thread messages   |
| Send Messages in Threads | Communicate inside modmail threads          |
| Create Public Threads    | Open a thread per report                    |
| Embed Links              | Send rich embeds                            |
| Manage Threads           | Archive and lock closed threads             |
| Read Message History     | Read thread messages                        |
| Mention Everyone         | Ping @everyone on new reports               |

---

## Required Privileged Intents

Enable these in the [Discord Developer Portal](https://discord.com/developers/applications) under your bot's settings:

| Intent                     | Reason                                            |
|----------------------------|---------------------------------------------------|
| **Server Members Intent**  | Detect role changes for auto onboarding DMs       |
| **Message Content Intent** | Read DM content for ModMail                       |

---

## Slash Commands

All commands are **Staff only** (Owner, Higher, or Staff role required).

### Moderation

| Command       | Options                    | Description                                                               |
|---------------|----------------------------|---------------------------------------------------------------------------|
| `/dm`         | `user`, `message`, `embed` | Send a private DM to any user. `embed` toggles styled embed (default: True). |
| `/say`        | `message`, `embed`         | Post a message in the current channel. `embed` toggles embed (default: False). |
| `/announce`   | `message`                  | Send a message to the announcements channel.                              |
| `/rules`      | `user`                     | Send a clickable rules channel mention to a user via DM.                  |
| `/dm_warning` | `user`, `reason`           | Send a formal **⚠️ warning embed** DM to a user with reason included.    |

### ModMail Management

| Command              | Options   | Description                                                   |
|----------------------|-----------|---------------------------------------------------------------|
| `/blacklist_add`     | `user_id` | Add a user ID to the ModMail blacklist.                       |
| `/blacklist_remove`  | `user_id` | Remove a user ID from the ModMail blacklist.                  |
| `/modmail_status`    | —         | Show count of active threads, pending, and blacklisted users. |

### The `embed` Parameter

| Command | embed default | Effect when True                         | Effect when False  |
|---------|---------------|------------------------------------------|--------------------|
| `/dm`   | `True`        | Sends a styled blurple embed with footer | Sends plain text   |
| `/say`  | `False`       | Sends a blurple embed in the channel     | Sends plain text   |

---

## ModMail System

The ModMail system lets server members privately contact staff by DMing the bot.

### User Flow

```
User sends any DM to the bot
        │
        ▼
Bot sends Support Embed
(How it works + What to include)
        │
   ┌────┴────┐
   │         │
Proceed    Cancel
   │         │
   ▼         ▼
"Ready to Help!"    Session
embed shown         ends
   │
   ▼
User sends their report message
        │
        ▼
Thread created in report channel
@everyone pinged
Action buttons posted
User receives "✅ Request Received" embed
```

### Session States

| State       | Description                                                                         |
|-------------|-------------------------------------------------------------------------------------|
| No session  | User has never DM'd or previous session ended. Bot shows support embed.             |
| Pending     | User clicked Proceed. Awaiting their report message. Times out in 5 minutes.        |
| Active      | Thread exists. User's DMs are forwarded to the thread.                              |
| Expired     | Pending state timed out after 5 minutes. User receives "⏱️ Session Expired" embed. |
| Closed      | Staff clicked Close. Thread archived/locked. User receives "🔒 Request Closed" embed.|
| Blacklisted | User is permanently blocked from creating new reports.                              |

### Inactivity Timeout

- If a user clicks **Proceed** but does not send a message within **5 minutes**, the session expires automatically.
- The bot sends a styled **⏱️ Session Expired** embed to the user.

### Two-Way Communication

| Direction          | How                                                                              |
|--------------------|----------------------------------------------------------------------------------|
| User → Staff       | User DMs the bot → forwarded as embed to the thread                             |
| Staff → User       | Staff types in the thread → forwarded as embed to the user's DM                 |
| Staff → User (btn) | Staff clicks Reply → fills modal → message sent to user's DM                   |

### Attachment Support

- Images are inlined in embeds directly.
- Multiple images in a single message are all forwarded (up to 10 embeds).
- Non-image attachments are listed as URLs.

---

## Staff Buttons

Buttons appear on the report embed in the report channel **and** inside the thread.
They work from either location. All buttons are visible only to staff.

| Button        | Action                                                                                                |
|---------------|-------------------------------------------------------------------------------------------------------|
| **Reply**     | Opens a text modal. Typed message is sent to the user's DM as a staff reply embed. Echoed into thread.|
| **Warn**      | Opens a user select menu, then a reason modal. Sends a warning DM. Logged.                           |
| **Mute**      | Opens a user select menu, then a reason modal. **Log only — does not apply a mute.**                 |
| **Ban**       | Opens a user select menu, then a reason modal. **Log only — does not apply a ban.**                  |
| **Close**     | Clears the user's session, sends "🔒 Request Closed" embed to user, archives + locks the thread.     |
| **Blacklist** | Adds the user to the blacklist permanently. Session is cleared. Cannot open new requests.            |

> **Note:** Mute and Ban are log-only. Apply those actions manually in Discord.

---

## Automatic Behaviours

All automatic DMs are sent as **rich embeds** with the server icon thumbnail, timestamp, and branded footer.

### Staff Role Promotion DM

When a member is **given** a Staff, Higher, or Owner role, the bot automatically:
1. Sends a **🎉 Congratulations on Your Promotion!** embed with:
   - Role name and server name
   - Link to the [Staff Guidelines](https://discord.com/channels/1318933846779101215/1486423070406213672/1487776297706061957)
   - Next steps to follow
2. Logs the promotion in the log channel.

### Staff Role Demotion DM

When a member **loses** a Staff, Higher, or Owner role, the bot automatically:
1. Sends a **📉 Staff Role Update** embed with:
   - Role removed and server name
   - What to do next / who to contact
2. Logs the demotion in the log channel.

### Event Manager Welcome DM

When a member is **given** the Event Manager role, the bot automatically:
1. Sends a **🎊 Welcome, Event Manager!** embed with:
   - Personalised welcome message
   - Link to the [Staff Guidelines](https://discord.com/channels/1318933846779101215/1486423070406213672/1487776297706061957)
   - Role and server fields
2. Logs the auto DM in the log channel.

### Precious Member Welcome DM

When a member is **given** the Precious Member role, the bot automatically:
1. Sends a **💎 Welcome, Precious Member!** embed listing their perks:
   - ✅ Can manage nicknames
   - ✅ Can create threads
   - ✅ Can make polls
   - ✅ Can upload stickers & emojis
2. Logs the auto DM in the log channel.

> In all cases, if the member has DMs disabled the bot logs a warning instead.

---

## Log System

All actions are posted to the log channel as **rich colour-coded embeds**.
Each embed has a title, **Target** and **Staff** inline fields, an optional **Reason** field, a timestamp, and a `DungeonKeeper Logs` footer.

### ModMail Logs

| Action                    | Title                  | Colour  |
|---------------------------|------------------------|---------|
| New report opened         | 📬 New Report          | Blurple |
| Staff reply sent          | 💬 Staff Reply         | Green   |
| Thread closed             | 🔒 Thread Closed       | Red     |
| User blacklisted (button) | 🚫 User Blacklisted    | Red     |
| `/blacklist_add`          | 🚫 Blacklist Added     | Red     |
| `/blacklist_remove`       | ✅ Blacklist Removed   | Green   |

### Moderation Logs

| Action               | Title               | Colour  |
|----------------------|---------------------|---------|
| Warning modal        | ⚠️ Warning Issued   | Yellow  |
| Mute modal (log)     | 🔇 Mute Logged      | Yellow  |
| Ban modal (log)      | 🔨 Ban Logged       | Red     |
| `/dm`                | 📨 DM Sent          | Blurple |
| `/dm_warning`        | ⚠️ Warning DM       | Yellow  |
| `/say`               | 📢 Message Posted   | Blurple |
| `/announce`          | 📣 Announcement     | Blurple |
| `/rules`             | 📋 Rules Sent       | Blurple |

### Role Event Logs

| Action                   | Title                    | Colour  |
|--------------------------|--------------------------|---------|
| Staff role given         | 🎉 Promotion             | Green   |
| Staff role removed       | 📉 Demotion              | Red     |
| Promotion DM failed      | ⚠️ Promotion DM Failed   | Yellow  |
| Demotion DM failed       | ⚠️ Demotion DM Failed    | Yellow  |
| Auto DM sent (any role)  | 📨 Auto DM Sent          | Blurple |
| Auto DM failed           | ⚠️ Auto DM Failed        | Yellow  |

---

## Data Storage

ModMail data is stored in `modmail_data.json` (auto-created on first use).

```json
{
  "sessions": {
    "user_id": {
      "thread_id": 123456789,
      "message_id": 987654321
    }
  },
  "blacklist": [111222333, 444555666]
}
```

| Field       | Description                                                             |
|-------------|-------------------------------------------------------------------------|
| `sessions`  | Maps user IDs to their active report thread and channel message         |
| `blacklist` | List of user IDs permanently blocked from the support system            |

Sessions survive bot restarts. The pending state is **in-memory only** and resets on restart — those users will need to DM the bot again.

---

## Channel & Role IDs

| Name                  | ID                    |
|-----------------------|-----------------------|
| Guild                 | `1318933846779101215` |
| Report Channel        | `1410225154239238184` |
| Log Channel           | `1487777995623235624` |
| Moderation Channel    | `1486423070406213672` |
| Announcements Channel | `1323890538881093735` |
| Owner Role            | `1456687923062767686` |
| Higher Role           | `1459898023365709934` |
| Staff Role            | `1318941651061833851` |
| Event Manager Role    | `1338922160227483690` |
| Precious Member Role  | `1330041993782624337` |

---

## Deployment

See **[GUIDE.md](GUIDE.md)** for full instructions covering:

- ▶️ Running locally
- ☁️ Free hosting on **Railway** or **Render**
- 💰 Paid VPS on **Hostinger**, **DigitalOcean**, or **Vultr**
- 📦 What to include when selling/handing off the bot

---

## File Structure

```
ModMail/
├── main.py              — Entire bot: slash commands, ModMail, auto-DMs, events
├── modmail_data.json    — Persistent session and blacklist data (auto-created)
├── requirements.txt     — Python dependencies
├── .env                 — Bot token (not committed)
├── GUIDE.md             — Deployment & customisation guide
└── README.md            — This file
```
