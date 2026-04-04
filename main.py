import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import json
from datetime import datetime, timezone
import random
import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageOps
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# Config
GUILD_ID = 1318933846779101215
REPORT_CHANNEL_ID = 1410225154239238184
LOG_CHANNEL_ID = 1487777995623235624
MODERATION_CHANNEL_ID = 1486423070406213672
ANNOUNCEMENT_CHANNEL_ID = 1323890538881093735

OWNER_ROLE_ID = 1456687923062767686
HIGHER_ROLE_ID = 1459898023365709934
STAFF_ROLE_ID = 1318941651061833851
EVENT_MANAGER_ROLE_ID = 1338922160227483690
PRECIOUS_MEMBER_ROLE_ID = 1330041993782624337
PREMIUM_ROLE_ID = 1489595969782943804

STAFF_ROLE_IDS = {OWNER_ROLE_ID, HIGHER_ROLE_ID, STAFF_ROLE_ID}

GIFS = {
    "hug": [
        "https://static.klipy.com/mocha-and-milk-bears-cuddle.gif",
        "https://static.klipy.com/squish-hug.gif",
        "https://static.klipy.com/cat-2032.gif",
        "https://static.klipy.com/bunny-247.gif",
        "https://static.klipy.com/love-language-3.gif"
    ],
    "kick": [
        "https://static.klipy.com/kickers-caught.gif",
        "https://static.klipy.com/milk-and-mocha-bear-couple-96.gif",
        "https://static.klipy.com/wildfireuv-70.gif",
        "https://static.klipy.com/chifuyu-chifuyu-kick.gif",
        "https://static.klipy.com/oh-yeah-high-kick.gif"
    ],
    "kiss": [
        "https://static.klipy.com/kiss-video-love-you.gif",
        "https://static.klipy.com/puuung-kiss-10.gif",
        "https://static.klipy.com/mwah-38.gif"
    ],
    "slap": [
        "https://static.klipy.com/dungeong-17.gif",
        "https://static.klipy.com/orange-cat-cat-hitting-cat.gif",
        "https://static.klipy.com/penguin-slap-4.gif",
        "https://static.klipy.com/slap-slaps-2.gif",
        "https://static.klipy.com/peach-and-goma-peach-cat-2.gif"
    ]
}
STAFF_RULES_LINK = "https://discord.com/channels/1318933846779101215/1486423070406213672/1487776297706061957"
TIMEOUT_SECONDS = 300
DATA_FILE = "modmail_data.json"

# In-memory session state
_pending: set[int] = set()
_timers: dict[int, asyncio.Task] = {}

def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"sessions": {}, "blacklist": []}
    with open(DATA_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {"sessions": {}, "blacklist": []}
    data.setdefault("sessions", {})
    data.setdefault("blacklist", [])
    return data

def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_uid(channel_id: int, message_id: int) -> int | None:
    data = load_data()
    for uid_str, session in data["sessions"].items():
        if isinstance(session, dict):
            if session.get("thread_id") == channel_id or session.get("message_id") == message_id:
                return int(uid_str)
        else:
            if session == channel_id:
                return int(uid_str)
    return None

def get_thread_id_for_user(user_id: int) -> int | None:
    data = load_data()
    session = data["sessions"].get(str(user_id))
    if isinstance(session, dict):
        return session.get("thread_id")
    return session

def is_staff(member: discord.Member) -> bool:
    return any(r.id in STAFF_ROLE_IDS for r in member.roles)

def _cancel_timer(uid: int):
    t = _timers.pop(uid, None)
    if t and not t.done():
        t.cancel()

async def _expire(uid: int, user: discord.User):
    await asyncio.sleep(TIMEOUT_SECONDS)
    _pending.discard(uid)
    _timers.pop(uid, None)
    try:
        embed = discord.Embed(
            title="⏱️ Session Expired",
            description="Your session timed out due to inactivity.\nPlease DM us again whenever you are ready.",
            color=discord.Color.orange(),
        )
        embed.set_footer(text="DungeonKeeper Moderation Team")
        await user.send(embed=embed)
    except discord.Forbidden:
        pass

def _start_timer(uid: int, user: discord.User):
    _cancel_timer(uid)
    _timers[uid] = asyncio.create_task(_expire(uid, user))

_LOG_META: dict[str, tuple[str, discord.Color]] = {
    # ModMail
    "opened":              ("📬 New Report",          discord.Color.from_str("#5865F2")),
    "reply":               ("💬 Staff Reply",          discord.Color.from_str("#57F287")),
    "close":               ("🔒 Thread Closed",        discord.Color.from_str("#ED4245")),
    "blacklist":           ("🚫 User Blacklisted",     discord.Color.from_str("#ED4245")),
    "blacklist_added":     ("🚫 Blacklist Added",      discord.Color.from_str("#ED4245")),
    "blacklist_removed":   ("✅ Blacklist Removed",    discord.Color.from_str("#57F287")),
    # Moderation
    "warn":                ("⚠️ Warning Issued",       discord.Color.from_str("#FEE75C")),
    "mute":                ("🔇 Mute Logged",          discord.Color.from_str("#FEE75C")),
    "ban":                 ("🔨 Ban Logged",            discord.Color.from_str("#ED4245")),
    "dm":                  ("📨 DM Sent",              discord.Color.from_str("#5865F2")),
    "dm_warning":          ("⚠️ Warning DM",           discord.Color.from_str("#FEE75C")),
    "say":                 ("📢 Message Posted",       discord.Color.from_str("#5865F2")),
    "announce":            ("📣 Announcement",         discord.Color.from_str("#5865F2")),
    "rules_dm":            ("📋 Rules Sent",           discord.Color.from_str("#5865F2")),
    # Role events
    "promotion":           ("🎉 Promotion",            discord.Color.from_str("#57F287")),
    "demotion":            ("📉 Demotion",             discord.Color.from_str("#ED4245")),
    "promotion_dm_fail":   ("⚠️ Promotion DM Failed", discord.Color.from_str("#FEE75C")),
    "demotion_dm_fail":    ("⚠️ Demotion DM Failed",  discord.Color.from_str("#FEE75C")),
    "auto_dm":             ("📨 Auto DM Sent",         discord.Color.from_str("#5865F2")),
    "auto_dm_fail":        ("⚠️ Auto DM Failed",       discord.Color.from_str("#FEE75C")),
}

async def log(guild: discord.Guild, action: str, staff: str, target: str, reason: str = ""):
    ch = guild.get_channel(LOG_CHANNEL_ID)
    if not ch:
        return

    title, color = _LOG_META.get(action.lower(), (f"🔹 {action.replace('_', ' ').title()}", discord.Color.greyple()))

    embed = discord.Embed(title=title, color=color, timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Target", value=target, inline=True)
    embed.add_field(name="Staff", value=staff, inline=True)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text="DungeonKeeper Logs")
    await ch.send(embed=embed)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class EntryView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=TIMEOUT_SECONDS)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.success)
    async def proceed(self, interaction: discord.Interaction, _: discord.ui.Button):
        uid = interaction.user.id
        data = load_data()
        if str(uid) in data["sessions"]:
            guild = interaction.client.get_guild(GUILD_ID)
            thread_id = get_thread_id_for_user(uid)
            if guild and thread_id and guild.get_thread(thread_id):
                already_embed = discord.Embed(
                    title="Already Open",
                    description="You already have an open support thread. Send a message here to continue it.",
                    color=discord.Color.orange(),
                )
                await interaction.response.edit_message(content=None, embed=already_embed, view=None)
                self.stop()
                return
            else:
                del data["sessions"][str(uid)]
                save_data(data)

        _pending.add(uid)
        _start_timer(uid, interaction.user)

        ready_embed = discord.Embed(
            title="🎫 Ready to Help!",
            description="Please describe your issue or question in detail.\nOur staff team will get back to you shortly.",
            color=discord.Color.from_str("#5865F2"),
        )
        ready_embed.add_field(
            name="💡 Tips for better support",
            value=(
                "• Be specific about the problem\n"
                "• Include any error messages\n"
                "• Mention what you already tried\n"
                "• Add screenshots if helpful"
            ),
            inline=False,
        )
        ready_embed.set_footer(text="Just send your message below ↓")
        await interaction.response.edit_message(content=None, embed=ready_embed, view=None)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        _cancel_timer(interaction.user.id)
        _pending.discard(interaction.user.id)
        await interaction.response.edit_message(content="Cancelled. DM us again if you need help.", embed=None, view=None)
        self.stop()

    async def on_timeout(self):
        _pending.discard(self.user_id)
        _cancel_timer(self.user_id)

class ReplyModal(discord.ui.Modal, title="Reply to User"):
    message = discord.ui.TextInput(label="Message", style=discord.TextStyle.paragraph, placeholder="Write your reply here...")
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            user = await interaction.client.fetch_user(self.user_id)
            embed = discord.Embed(description=self.message.value, color=discord.Color.blurple())
            embed.set_author(name=f"{interaction.guild.name} Staff Reply")
            await user.send(embed=embed)
            await interaction.channel.send(f"Reply sent to {user.mention}: {self.message.value}")
            await log(interaction.guild, "reply", str(interaction.user), str(user), self.message.value[:200])
            await interaction.followup.send("Reply sent.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Could not DM the user (DMs closed).", ephemeral=True)

class ActionModal(discord.ui.Modal):
    reason = discord.ui.TextInput(label="Reason", style=discord.TextStyle.paragraph)
    
    def __init__(self, action: str, target: discord.User):
        super().__init__(title=f"{action.capitalize()} Reason")
        self.action = action
        self.target = target

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if self.action == "warn":
            try:
                await self.target.send(f"You have been warned.\n\nReason: {self.reason.value}\n\nContact staff in <#{MODERATION_CHANNEL_ID}> for details.")
            except discord.Forbidden:
                pass
        await log(interaction.guild, self.action, str(interaction.user), str(self.target), self.reason.value)
        await interaction.followup.send(f"{self.action.capitalize()} logged for {self.target.mention}.", ephemeral=True)

class UserSelectView(discord.ui.View):
    def __init__(self, action: str):
        super().__init__(timeout=60)
        self.action = action

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Select a user...", min_values=1, max_values=1)
    async def pick(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        try:
            # We select a user, fetch them to pass to the modal
            user = await interaction.client.fetch_user(select.values[0].id)
            await interaction.response.send_modal(ActionModal(self.action, user))
        except Exception:
            await interaction.response.send_message("Invalid user selected.", ephemeral=True)
        self.stop()

class ThreadView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member) or not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can use these buttons.", ephemeral=True)
            return False
        return True

    def _uid(self, interaction: discord.Interaction) -> int | None:
        return get_uid(interaction.channel_id, interaction.message.id)

    @discord.ui.button(label="Reply", style=discord.ButtonStyle.primary, custom_id="mm:reply")
    async def reply(self, interaction: discord.Interaction, _: discord.ui.Button):
        uid = self._uid(interaction)
        if not uid: return await interaction.response.send_message("No active session found.", ephemeral=True)
        await interaction.response.send_modal(ReplyModal(uid))

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.secondary, custom_id="mm:warn")
    async def warn(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_message("Select user to warn:", view=UserSelectView("warn"), ephemeral=True)

    @discord.ui.button(label="Mute", style=discord.ButtonStyle.secondary, custom_id="mm:mute")
    async def mute(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_message("Select user to mute:", view=UserSelectView("mute"), ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger, custom_id="mm:ban")
    async def ban(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_message("Select user to ban:", view=UserSelectView("ban"), ephemeral=True)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="mm:close")
    async def close(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        uid = self._uid(interaction)
        if uid:
            data = load_data()
            data["sessions"].pop(str(uid), None)
            save_data(data)
            try:
                user = await interaction.client.fetch_user(uid)
                embed = discord.Embed(
                    title="🔒 Request Closed",
                    description="Your support request has been reviewed and closed by our staff team.\n\nIf you have a new issue, feel free to DM us again.",
                    color=discord.Color.from_str("#5865F2"),
                )
                embed.set_footer(text="DungeonKeeper Moderation Team")
                await user.send(embed=embed)
            except discord.Forbidden:
                pass
            await log(interaction.guild, "close", str(interaction.user), f"<@{uid}>")
        
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.edit(name=f"[closed] {interaction.channel.name}", archived=True, locked=True)
        await interaction.followup.send("Thread closed.", ephemeral=True)

    @discord.ui.button(label="Blacklist", style=discord.ButtonStyle.danger, custom_id="mm:blacklist")
    async def blacklist(self, interaction: discord.Interaction, _: discord.ui.Button):
        uid = self._uid(interaction)
        if not uid: return await interaction.response.send_message("No active session found.", ephemeral=True)
        data = load_data()
        if uid in data["blacklist"]:
            return await interaction.response.send_message("User is already blacklisted.", ephemeral=True)
        data["blacklist"].append(uid)
        data["sessions"].pop(str(uid), None)
        save_data(data)
        await log(interaction.guild, "blacklist", str(interaction.user), f"<@{uid}>")
        await interaction.response.send_message(f"User <@{uid}> has been blacklisted.", ephemeral=True)

class DungeonKeeperBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=["!", "-"], intents=intents)

    async def setup_hook(self):
        self.add_view(ThreadView())
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
        print("Slash commands synced.")

bot = DungeonKeeperBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    print(f"Debug: Member update for {after.display_name} - Roles: {[r.id for r in after.roles]}")
    before_roles = set(r.id for r in before.roles)
    after_roles  = set(r.id for r in after.roles)

    added   = (after_roles  - before_roles) & STAFF_ROLE_IDS
    removed = (before_roles - after_roles)  & STAFF_ROLE_IDS

    for role_id in added:
        role_obj  = after.guild.get_role(role_id)
        role_name = role_obj.name if role_obj else "Staff"
        try:
            promo_embed = discord.Embed(
                title="🎉 Congratulations on Your Promotion!",
                description=(
                    f"Welcome to the team, **{after.display_name}**! 🏆\n\n"
                    f"You have been promoted to **⚒️ {role_name}** in **{after.guild.name}**.\n"
                    f"We are thrilled to have you as part of the staff!"
                ),
                color=discord.Color.from_str("#57F287"),
                timestamp=datetime.now(timezone.utc),
            )
            promo_embed.add_field(
                name="📋 Next Steps",
                value=(
                    "• Review the [Staff Guidelines](" + STAFF_RULES_LINK + ")\n"
                    "• Uphold and enforce our community standards\n"
                    "• Reach out to senior staff if you have any questions"
                ),
                inline=False,
            )
            promo_embed.add_field(
                name="🛡️ Your New Role",
                value=f"⚒️ {role_name}",
                inline=True,
            )
            promo_embed.add_field(
                name="🏰 Server",
                value=after.guild.name,
                inline=True,
            )
            promo_embed.set_thumbnail(url=after.guild.icon.url if after.guild.icon else after.display_avatar.url)
            promo_embed.set_footer(text="DungeonKeeper Moderation Team • Congratulations! 🎊")
            await after.send(embed=promo_embed)
            await log(after.guild, "promotion", "System", str(after), f"Promoted to {role_name}")
        except discord.Forbidden:
            await log(after.guild, "promotion_dm_fail", "System", str(after), "DMs disabled")

    for role_id in removed:
        role_obj  = after.guild.get_role(role_id)
        role_name = role_obj.name if role_obj else "Staff"
        try:
            demote_embed = discord.Embed(
                title="📉 Staff Role Update",
                description=(
                    f"Hi **{after.display_name}**,\n\n"
                    f"You have been demoted from **⚒️ {role_name}** in **{after.guild.name}**.\n"
                    f"If you have any questions regarding this decision, please reach out to a senior staff member."
                ),
                color=discord.Color.from_str("#ED4245"),
                timestamp=datetime.now(timezone.utc),
            )
            demote_embed.add_field(
                name="❓ What Now?",
                value=(
                    "• Contact a senior staff member for clarification\n"
                    "• Continue following our community rules as a member\n"
                    "• You may be reconsidered for staff in the future"
                ),
                inline=False,
            )
            demote_embed.add_field(
                name="📌 Role Removed",
                value=f"⚒️ {role_name}",
                inline=True,
            )
            demote_embed.add_field(
                name="🏰 Server",
                value=after.guild.name,
                inline=True,
            )
            demote_embed.set_thumbnail(url=after.guild.icon.url if after.guild.icon else after.display_avatar.url)
            demote_embed.set_footer(text="DungeonKeeper Moderation Team • We wish you well.")
            await after.send(embed=demote_embed)
            await log(after.guild, "demotion", "System", str(after), f"Demoted from {role_name}")
        except discord.Forbidden:
            await log(after.guild, "demotion_dm_fail", "System", str(after), "DMs disabled")

    # ── Event Manager welcome ──────────────────────────────────────────────
    if EVENT_MANAGER_ROLE_ID in (after_roles - before_roles):
        role_obj  = after.guild.get_role(EVENT_MANAGER_ROLE_ID)
        role_name = role_obj.name if role_obj else "Event Manager"
        try:
            em_embed = discord.Embed(
                title="🎊 Welcome, Event Manager!",
                description=(
                    f"Hey **{after.display_name}**! 🎉\n\n"
                    f"You've been granted the **{role_name}** role in **{after.guild.name}**.\n"
                    f"We're excited to have you helping shape our community events!"
                ),
                color=discord.Color.from_str("#5865F2"),
                timestamp=datetime.now(timezone.utc),
            )
            em_embed.add_field(
                name="📋 Before You Start",
                value=(
                    f"• Review the [Staff Guidelines]({STAFF_RULES_LINK})\n"
                    "• Uphold and follow our community standards\n"
                    "• Reach out to senior staff with any questions"
                ),
                inline=False,
            )
            em_embed.add_field(
                name="🎭 Your Role",
                value=role_name,
                inline=True,
            )
            em_embed.add_field(
                name="🏰 Server",
                value=after.guild.name,
                inline=True,
            )
            em_embed.set_thumbnail(url=after.guild.icon.url if after.guild.icon else after.display_avatar.url)
            em_embed.set_footer(text="DungeonKeeper • Welcome aboard! 🎊")
            await after.send(embed=em_embed)
            await log(after.guild, "auto_dm", "System", str(after), f"Event Manager welcome sent")
        except discord.Forbidden:
            await log(after.guild, "auto_dm_fail", "System", str(after), "DMs disabled – Event Manager welcome")

    # ── Precious Member welcome ────────────────────────────────────────────
    if PRECIOUS_MEMBER_ROLE_ID in (after_roles - before_roles):
        role_obj  = after.guild.get_role(PRECIOUS_MEMBER_ROLE_ID)
        role_name = role_obj.name if role_obj else "Precious Member"
        try:
            pm_embed = discord.Embed(
                title="💎 Welcome, Precious Member!",
                description=(
                    f"Hey **{after.display_name}**! ✨\n\n"
                    f"You've been granted the **{role_name}** role in **{after.guild.name}**.\n"
                    f"Thank you for being a valued part of our community!"
                ),
                color=discord.Color.from_str("#F1C40F"),
                timestamp=datetime.now(timezone.utc),
            )
            pm_embed.add_field(
                name=f"🎁 What You Get as a {role_name}",
                value=(
                    "✅ Can manage nicknames\n"
                    "✅ Can create threads\n"
                    "✅ Can make polls\n"
                    "✅ Can upload stickers & emojis"
                ),
                inline=False,
            )
            pm_embed.set_thumbnail(url=after.guild.icon.url if after.guild.icon else after.display_avatar.url)
            pm_embed.set_footer(text="DungeonKeeper • We appreciate you! 💛")
            await after.send(embed=pm_embed)
            await log(after.guild, "auto_dm", "System", str(after), f"Precious Member welcome sent")
        except discord.Forbidden:
            await log(after.guild, "auto_dm_fail", "System", str(after), "DMs disabled – Precious Member welcome")

    # ── Premium Member Flow ────────────────────────────────────────────────
    if PREMIUM_ROLE_ID in (after_roles - before_roles):
        try:
            premium_embed = discord.Embed(
                title="🎉 Purchase Successful! Welcome to Premium!",
                description=(
                    "Here’s everything you unlock:\n\n"
                    "👑 **Exclusive Access**\n"
                    "• Access to premium-only channels\n"
                    "• Priority support & faster responses\n"
                    "• Early access to new features\n\n"
                    "🎨 **Customization**\n"
                    "• Custom role (DM admin to set name/color/icon)\n"
                    "• Use external emojis & stickers\n"
                    "• Send embeds, links, and media freely\n\n"
                    "🤖 **Premium Bot Commands**\n"
                    "• `-kick @user` – Fun kick GIF interaction\n"
                    "• `-slap @user` – Random slap GIF\n"
                    "• `-hug @user` – Wholesome hug GIF\n"
                    "• `-kiss @user` – Sweet kiss GIF\n"
                    "• `-ship @user` – Compatibility match image 💖\n\n"
                    "🎭 **Extra Permissions**\n"
                    "• Create private/public threads\n"
                    "• Send voice messages\n"
                    "• Create polls\n"
                    "• Use activities in voice channels\n"
                    "• Use soundboard & external sounds\n\n"
                    "✨ **Enjoy your premium experience and have fun!**"
                ),
                color=discord.Color.blurple(),
                timestamp=datetime.now(timezone.utc),
            )
            premium_embed.set_thumbnail(url=after.guild.icon.url if after.guild.icon else after.display_avatar.url)
            premium_embed.set_footer(text="DungeonKeeper Premium Team • We're glad you're here! 💎")
            await after.send(embed=premium_embed)
            await log(after.guild, "auto_dm", "System", str(after), "Premium purchase DM sent")
        except discord.Forbidden:
            await log(after.guild, "auto_dm_fail", "System", str(after), "DMs disabled – Premium purchase")

    if PREMIUM_ROLE_ID in (before_roles - after_roles):
        try:
            expiry_embed = discord.Embed(
                title="⚠️ Your Premium Subscription Has Ended",
                description=(
                    "Your perks and premium role have been removed.\n\n"
                    "We hope you enjoyed your experience 💙\n"
                    "You can always rejoin Premium anytime!"
                ),
                color=discord.Color.from_str("#ED4245"),
                timestamp=datetime.now(timezone.utc),
            )
            expiry_embed.set_footer(text="DungeonKeeper Premium Team • See you soon!")
            await after.send(embed=expiry_embed)
            await log(after.guild, "auto_dm", "System", str(after), "Premium expiry DM sent")
        except discord.Forbidden:
            await log(after.guild, "auto_dm_fail", "System", str(after), "DMs disabled – Premium expiry")

def _support_embed() -> discord.Embed:
    e = discord.Embed(
        title="DungeonKeeper Support System",
        description="Welcome. Our staff team will assist you.\nPlease read the guidelines below before proceeding.",
        color=discord.Color.from_str("#5865F2"),
    )
    e.add_field(name="How it works", value="- Describe your issue clearly\n- Staff will review and respond\n- Your conversation is private", inline=False)
    e.add_field(name="What to include", value="- Username of the member\n- What happened\n- Evidence (screenshots if available)", inline=False)
    return e

async def handle_dm(message: discord.Message):
    user = message.author
    uid = user.id
    data = load_data()

    if uid in data["blacklist"]:
        return

    uid_str = str(uid)
    if uid_str in data["sessions"]:
        guild = bot.get_guild(GUILD_ID)
        thread_id = get_thread_id_for_user(uid)
        thread = guild.get_thread(thread_id) if guild and thread_id else None
        if thread:
            await forward_dm(message, user, thread)
            return
        else:
            del data["sessions"][uid_str]
            save_data(data)

    if uid in _pending:
        _pending.discard(uid)
        _cancel_timer(uid)
        await create_thread(message, user)
        return

    await message.channel.send(embed=_support_embed(), view=EntryView(uid))

async def forward_dm(message: discord.Message, user: discord.User, thread: discord.Thread):
    embeds = []
    main_embed = discord.Embed(description=message.content or "*[No text]*", color=discord.Color.blue())
    main_embed.set_author(name=f"{user.display_name} ({user.id})", icon_url=user.display_avatar.url)
    
    image_attachments = []
    other_attachments = []
    
    for a in message.attachments:
        if a.content_type and a.content_type.startswith("image/"):
            image_attachments.append(a)
        else:
            other_attachments.append(a)
            
    if other_attachments:
        main_embed.add_field(name="Attachments", value="\n".join(a.url for a in other_attachments), inline=False)
        
    if image_attachments:
        main_embed.set_image(url=image_attachments[0].url)
        embeds.append(main_embed)
        for a in image_attachments[1:]:
            extra = discord.Embed(color=discord.Color.blue())
            extra.set_image(url=a.url)
            embeds.append(extra)
    else:
        embeds.append(main_embed)

    await thread.send(embeds=embeds[:10])

async def create_thread(message: discord.Message, user: discord.User):
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        err_embed = discord.Embed(
            title="❌ Error",
            description="Something went wrong on our end. Please try again in a moment.",
            color=discord.Color.red(),
        )
        err_embed.set_footer(text="DungeonKeeper Moderation Team")
        await message.channel.send(embed=err_embed)
        return

    report_ch = guild.get_channel(REPORT_CHANNEL_ID)
    if not report_ch:
        return

    embed = discord.Embed(
        title=f"New Report: {user.display_name}",
        color=discord.Color.red(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name="User", value=f"{user.mention} (`{user.id}`)", inline=False)
    embed.add_field(name="Message", value=message.content or "*[No text - see attachments]*", inline=False)
    
    embeds = []
    image_attachments = []
    other_attachments = []
    
    for a in message.attachments:
        if a.content_type and a.content_type.startswith("image/"):
            image_attachments.append(a)
        else:
            other_attachments.append(a)
            
    if other_attachments:
        embed.add_field(name="Attachments", value="\n".join(a.url for a in other_attachments), inline=False)

    if image_attachments:
        embed.set_image(url=image_attachments[0].url)
        embeds.append(embed)
        for a in image_attachments[1:]:
            extra = discord.Embed(color=discord.Color.red())
            extra.set_image(url=a.url)
            embeds.append(extra)
    else:
        embeds.append(embed)

    report_msg = await report_ch.send(
        content="@everyone",
        embeds=embeds[:10],
        view=ThreadView(),
        allowed_mentions=discord.AllowedMentions(everyone=True),
    )
    thread = await report_msg.create_thread(name=f"report-{user.name[:30]}")

    data = load_data()
    data["sessions"][str(user.id)] = {"thread_id": thread.id, "message_id": report_msg.id}
    save_data(data)

    await thread.send("Manage this report using the buttons below.", view=ThreadView())
    await log(guild, "opened", "System", str(user), message.content[:100] if message.content else "")
    confirm_embed = discord.Embed(
        title="✅ Request Received",
        description="Your message has been sent to the **Moderation Team**.\nA staff member will respond to you as soon as possible.",
        color=discord.Color.green(),
    )
    confirm_embed.add_field(
        name="What happens next?",
        value="• Staff will review your request\n• You will receive a reply here in DMs\n• You can send follow-up messages at any time",
        inline=False,
    )
    confirm_embed.set_footer(text="DungeonKeeper Moderation Team")
    await message.channel.send(embed=confirm_embed)

async def handle_thread(message: discord.Message):
    uid = get_uid(message.channel.id, 0)
    if not uid: return
    member = message.guild.get_member(message.author.id)
    if not member or not is_staff(member): return
    
    try:
        user = await bot.fetch_user(uid)
        
        embeds = []
        main_embed = discord.Embed(description=message.content or "*[No text]*", color=discord.Color.blurple())
        main_embed.set_author(name=f"{message.guild.name} Staff Reply")
        
        image_attachments = []
        other_attachments = []
        for a in message.attachments:
            if a.content_type and a.content_type.startswith("image/"):
                image_attachments.append(a)
            else:
                other_attachments.append(a)
                
        if other_attachments:
            main_embed.add_field(name="Attachments", value="\n".join(a.url for a in other_attachments), inline=False)
            
        if image_attachments:
            main_embed.set_image(url=image_attachments[0].url)
            embeds.append(main_embed)
            for a in image_attachments[1:]:
                extra = discord.Embed(color=discord.Color.blurple())
                extra.set_image(url=a.url)
                embeds.append(extra)
        else:
            embeds.append(main_embed)

        await user.send(embeds=embeds[:10])
        await log(message.guild, "reply", str(message.author), str(user), message.content[:200] if message.content else "")
    except discord.Forbidden:
        pass

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    print(f"Debug: Received message from {message.author}: {message.content}")

    # DM flow
    if message.guild is None:
        await handle_dm(message)
        return

    # Thread forward
    if isinstance(message.channel, discord.Thread):
        await handle_thread(message)
    
    await bot.process_commands(message)

def staff_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        if is_staff(interaction.user):
            return True
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return False
    return app_commands.check(predicate)

@bot.tree.command(name="dm", description="Send a DM to a user.")
@app_commands.describe(user="The user to DM", message="The message to send", embed="Send as an embed? (default: True)")
@staff_only()
async def dm(interaction: discord.Interaction, user: discord.Member, message: str, embed: bool = True):
    try:
        if embed:
            e = discord.Embed(description=message, color=discord.Color.blurple())
            e.set_author(name=f"{interaction.guild.name} Staff")
            e.set_footer(text="DungeonKeeper Moderation Team")
            await user.send(embed=e)
        else:
            await user.send(f"**{interaction.guild.name} Staff:** {message}")
        await interaction.response.send_message(f"DM sent to {user.mention}.", ephemeral=True)
        await log(interaction.guild, "dm", str(interaction.user), str(user), message)
    except discord.Forbidden:
        await interaction.response.send_message(f"Could not DM {user.mention} (their DMs may be closed).", ephemeral=True)

@bot.tree.command(name="say", description="Send a message in the current channel.")
@app_commands.describe(message="The message to send", embed="Send as an embed? (default: False)")
@staff_only()
async def say(interaction: discord.Interaction, message: str, embed: bool = False):
    await interaction.response.defer(ephemeral=True)
    if embed:
        e = discord.Embed(description=message, color=discord.Color.blurple())
        e.set_footer(text=interaction.guild.name)
        await interaction.channel.send(embed=e)
    else:
        await interaction.channel.send(message)
    await log(interaction.guild, "say", str(interaction.user), interaction.channel.name, message)

@bot.tree.command(name="announce", description="Send an announcement to the announcements channel.")
@staff_only()
async def announce(interaction: discord.Interaction, message: str):
    channel = interaction.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if not channel:
        return await interaction.response.send_message("Announcement channel not found.", ephemeral=True)
    await channel.send(message)
    await interaction.response.send_message("Announcement sent.", ephemeral=True)
    await log(interaction.guild, "announce", str(interaction.user), channel.name, message)

@bot.tree.command(name="rules", description="Send the rules channel link to a user.")
@app_commands.describe(user="The user to send the rules to")
@staff_only()
async def rules(interaction: discord.Interaction, user: discord.Member):
    try:
        await user.send(
            f"Hey {user.display_name}, please review the rules here: <#1318959296884768798>"
        )
        await interaction.response.send_message(f"Rules link sent to {user.mention}.", ephemeral=True)
        await log(interaction.guild, "rules_dm", str(interaction.user), str(user))
    except discord.Forbidden:
        await interaction.response.send_message(f"Could not DM {user.mention} (their DMs may be closed).", ephemeral=True)

@bot.tree.command(name="dm_warning", description="Send a warning DM to a user.")
@staff_only()
async def dm_warning(interaction: discord.Interaction, user: discord.Member, reason: str):
    warn_embed = discord.Embed(
        title="⚠️ Official Warning",
        description=(
            f"Hey **{user.display_name}**,\n\n"
            f"You are receiving a warning from the **{interaction.guild.name}** staff team.\n"
            f"Please ensure you follow the server rules to avoid further action."
        ),
        color=discord.Color.from_str("#FEE75C"),
        timestamp=datetime.now(timezone.utc),
    )
    warn_embed.add_field(
        name="📋 Reason",
        value=reason,
        inline=False,
    )
    warn_embed.add_field(
        name="❓ Believe this is a mistake?",
        value=f"Contact a staff member in <#{MODERATION_CHANNEL_ID}>.",
        inline=False,
    )
    warn_embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else user.display_avatar.url)
    warn_embed.set_footer(text="DungeonKeeper Moderation Team")
    try:
        await user.send(embed=warn_embed)
        await interaction.response.send_message(f"Warning DM sent to {user.mention}.", ephemeral=True)
        await log(interaction.guild, "dm_warning", str(interaction.user), str(user), reason)
    except discord.Forbidden:
        await interaction.response.send_message(f"Could not DM {user.mention} (their DMs may be closed).", ephemeral=True)

@bot.tree.command(name="blacklist_add", description="Add a user ID to the ModMail blacklist.")
@staff_only()
async def blacklist_add(interaction: discord.Interaction, user_id: str):
    if not user_id.isdigit():
        return await interaction.response.send_message("Invalid user ID.", ephemeral=True)
    uid = int(user_id)
    data = load_data()
    if uid in data["blacklist"]:
        return await interaction.response.send_message("User is already blacklisted.", ephemeral=True)
    data["blacklist"].append(uid)
    data["sessions"].pop(str(uid), None)
    save_data(data)
    await interaction.response.send_message(f"Added {uid} to the blacklist.", ephemeral=True)
    await log(interaction.guild, "blacklist_added", str(interaction.user), str(uid))

@bot.tree.command(name="blacklist_remove", description="Remove a user ID from the ModMail blacklist.")
@staff_only()
async def blacklist_remove(interaction: discord.Interaction, user_id: str):
    if not user_id.isdigit():
        return await interaction.response.send_message("Invalid user ID.", ephemeral=True)
    uid = int(user_id)
    data = load_data()
    if uid not in data["blacklist"]:
        return await interaction.response.send_message("User is not blacklisted.", ephemeral=True)
    data["blacklist"].remove(uid)
    save_data(data)
    await interaction.response.send_message(f"Removed {uid} from the blacklist.", ephemeral=True)
    await log(interaction.guild, "blacklist_removed", str(interaction.user), str(uid))

@bot.tree.command(name="modmail_status", description="Check the status of ModMail system.")
@staff_only()
async def modmail_status(interaction: discord.Interaction):
    data = load_data()
    active_sessions = len(data.get("sessions", {}))
    blacklisted_users = len(data.get("blacklist", []))
    pending_users = len(_pending)
    
    embed = discord.Embed(title="ModMail Status", color=discord.Color.blue())
    embed.add_field(name="Active Threads", value=str(active_sessions), inline=True)
    embed.add_field(name="Pending Users", value=str(pending_users), inline=True)
    embed.add_field(name="Blacklisted Users", value=str(blacklisted_users), inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def _action_cmd(ctx: commands.Context, target: discord.Member, action_name: str, past_tense: str):
    await ctx.message.delete()
    gif_url = random.choice(GIFS[action_name])
    await ctx.send(f"{gif_url}\n{ctx.author.mention} {past_tense} {target.mention}")

def premium_only_cmd():
    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild: return False
        is_premium = any(r.id == PREMIUM_ROLE_ID for r in ctx.author.roles)
        print(f"Debug: Command check for {ctx.author.display_name} - IsPremium: {is_premium}")
        if is_premium or is_staff(ctx.author) or ctx.author.guild_permissions.administrator:
            return True
        await ctx.send("This command is exclusive to **Premium members**! 💎", delete_after=5)
        return False
    return commands.check(predicate)

@bot.command(name="hug")
@premium_only_cmd()
async def hug_cmd(ctx: commands.Context, target: discord.Member):
    await _action_cmd(ctx, target, "hug", "hugged")

@bot.command(name="kick")
@premium_only_cmd()
async def kick_cmd(ctx: commands.Context, target: discord.Member):
    await _action_cmd(ctx, target, "kick", "kicked")

@bot.command(name="slap")
@premium_only_cmd()
async def slap_cmd(ctx: commands.Context, target: discord.Member):
    await _action_cmd(ctx, target, "slap", "slapped")

@bot.command(name="kiss")
@premium_only_cmd()
async def kiss_cmd(ctx: commands.Context, target: discord.Member):
    await _action_cmd(ctx, target, "kiss", "kissed")

async def create_ship_image(user1: discord.Member, user2: discord.Member, percentage: int) -> io.BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(user1.display_avatar.with_format("png").url) as r1, \
                   session.get(user2.display_avatar.with_format("png").url) as r2:
            img1 = Image.open(io.BytesIO(await r1.read())).convert("RGBA").resize((200, 200))
            img2 = Image.open(io.BytesIO(await r2.read())).convert("RGBA").resize((200, 200))

    canvas_w, canvas_h = 1000, 320
    base = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)

    # Simple gradient background
    for x in range(canvas_w):
        r = int(72 + (x / canvas_w) * 60)
        g = int(149 + (x / canvas_w) * 80)
        b = int(239 - (x / canvas_w) * 50)
        draw.line([(x, 0), (x, canvas_h)], fill=(r, g, b, 255))

    # Mask for circular avatars
    mask = Image.new("L", (200, 200), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 200, 200), fill=255)

    base.paste(img1, (100, 60), mask)
    base.paste(img2, (700, 60), mask)

    # Draw heart
    heart_center = (500, 160)
    draw.polygon([
        (500, 250), (430, 180), (430, 130), (465, 100), (500, 135),
        (535, 100), (570, 130), (570, 180)
    ], fill=(255, 105, 180, 255)) # Hot Pink

    # Draw percentage text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text = f"{percentage}%"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((heart_center[0] - tw/2, heart_center[1] - th/2), text, fill="white", font=font)

    buf = io.BytesIO()
    base.save(buf, format="PNG")
    buf.seek(0)
    return buf

@bot.command(name="ship")
@premium_only_cmd()
async def ship_cmd(ctx: commands.Context, target: discord.Member):
    await ctx.message.delete()
    percentage = random.randint(0, 100)
    
    async with ctx.typing():
        try:
            image_buf = await create_ship_image(ctx.author, target, percentage)
            file = discord.File(fp=image_buf, filename="ship.png")
            
            embed = discord.Embed(
                title="💞 Compatibility Match",
                description=f"**{ctx.author.display_name}** and **{target.display_name}** are a **{percentage}%** match!",
                color=discord.Color.from_str("#FF69B4")
            )
            embed.set_image(url="attachment://ship.png")
            await ctx.send(file=file, embed=embed)
        except Exception:
            await ctx.send(f"💞 **{ctx.author.display_name}** x **{target.display_name}**: **{percentage}%**!")

if __name__ == "__main__":
    bot.run(TOKEN)
