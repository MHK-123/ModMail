# DungeonKeeper Bot Commands

This document lists all available commands for the DungeonKeeper bot, separated by category.

---

## 🛡️ Staff Commands (Slash Commands)
These commands require the user to have the **Owner**, **Higher Staff**, or **Staff** role.

### `/dm`
Sends a direct message to a specific user through the bot.
- **Parameters**: 
  - `user`: The member you want to message.
  - `message`: The content of the message.
  - `embed`: (Optional) Whether to send the message as a professional embed. (Defaults to `True`).

### `/say`
Sends a message in the current channel through the bot.
- **Parameters**:
  - `message`: The content of the message.
  - `embed`: (Optional) Whether to wrap the message in an embed. (Defaults to `False`).

### `/announce`
Broadcasts an announcement to the designated announcement channel.
- **Parameters**:
  - `message`: The text content of the announcement.
- *Sends to the channel defined as `ANNOUNCEMENT_CHANNEL_ID` in the config.*

### `/rules`
Sends a DM to a user with a link to the server's rules channel.
- **Parameters**:
  - `user`: The member you want to remind about the rules.

### `/dm_warning`
Sends an official warning message to a user via DM and logs the action.
- **Parameters**:
  - `user`: The member to receive the warning.
  - `reason`: The reason for the warning.

### `/blacklist_add`
Blocks a specific user ID from using the ModMail system.
- **Parameters**:
  - `user_id`: The unique Discord snowflake ID of the user to blacklist.

### `/blacklist_remove`
Removes a user ID from the ModMail blacklist.
- **Parameters**:
  - `user_id`: The unique Discord snowflake ID of the user to unblock.

### `/modmail_status`
Displays current ModMail usage statistics.
- **Parameters**: None.
- *Shows active threads, pending users, and the total number of blacklisted users.*

---

## 💎 Premium Commands (Prefix Commands)
These commands require the **Premium** role (or Staff/Admin permissions). They must be prefixed with `-` (or `!`).

### `-hug @user`
Sends a wholesome hug GIF, mentioning the target user.

### `-kick @user`
Sends a fun kick GIF, mentioning the target user.

### `-slap @user`
Sends a random slap GIF, mentioning the target user.

### `-kiss @user`
Sends a sweet kiss GIF, mentioning the target user.

### `-punch @user`
Sends an intense punch GIF, mentioning the target user.

### `-ship @user`
Generates a highly-customized, premium 1000x500 image showing the compatibility percentage between the command user and the target user. Includes glowing aesthetics and avatars.
