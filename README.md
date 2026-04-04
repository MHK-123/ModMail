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
  - `-ship @user`: Dynamic compatibility match image generation using a **Render-hosted FastAPI Rendering Service** (Playwright + HTML/CSS).

---

## 📚 Documentation

Detailed documentation has been separated into the `docs/` folder for better readability:

- [🤖 Bot Overview & Features](docs/overview.md)
- [📜 Complete Commands List](docs/commands.md)

---

## 🚀 Quick Start

### 📋 Prerequisites
- **Python 3.10+**
- **Discord Bot Token** (Intents: `Members`, `Message Content` enabled)
- **SHIP_RENDER_URL**: URL of your deployed image-rendering microservice (Render.com).
- **Role IDs**: Configured in `main.py` (Owner, Higher, Staff, Premium).

### 🛠️ Installation
1. **Deploy Render Service**: Use the provided `render-service/` folder to deploy to Render.com (using the `render.yaml` Blueprint).
2. **Setup Bot**: Clone the repository to your bot hosting (e.g., GitHub Actions):
   ```bash
   git clone https://github.com/MHK-123/ModMail.git
   cd ModMail
   ```
3. **Environment Setup**: Add your `DISCORD_TOKEN` and `SHIP_RENDER_URL` to your environment variables or GitHub Secrets.
4. **Install & Run**:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

---

## 🛠️ Configuration

The following IDs must be updated in `main.py`:
- `GUILD_ID`: Your Discord Server ID.
- `REPORT_CHANNEL_ID`: Channel where ModMail threads are created.
- `LOG_CHANNEL_ID`: Channel for bot action logs.
- `PREMIUM_ROLE_ID`: ID of the role that unlocks premium commands.
- `SHIP_RENDER_URL`: (Variable) The API endpoint for image generation.

---

## 📜 Credits & License
Developed for **DungeonKeeper**. Assets provided by **Klipy**.

