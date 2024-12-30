### **README.md**

# **Kasutamaiza Bot**

Kasutamaiza Bot is a powerful and modular Discord bot designed to enhance server engagement, provide utility features, and support Yu-Gi-Oh enthusiasts with custom commands. This document covers the progress made in **Step 1 of Phase 1**.

---

## **Table of Contents**

1. [Features](#features)
2. [Setup and Deployment](#setup-and-deployment)
3. [Commands](#commands)
4. [Cogs](#cogs)
5. [Technical Details](#technical-details)
6. [Roadmap](#roadmap)

---

## **Features**

- **Core Functionalities**:
  - 24/7 hosting on a reliable server (e.g., DigitalOcean).
  - Dynamic cog-based architecture for scalability and easy feature addition.
  - Slash commands scoped to specific guilds for efficient command management.

- **Diagnostics and Logging**:
  - `/diagnostics` command for detailed bot state, permissions, and environment checks.
  - Rotating logs with `loguru` for efficient error tracking and system monitoring.

- **Heartbeat**:
  - Periodic "heartbeat" messages in logs to confirm the bot is online and operational.

---

## **Setup and Deployment**

### **Prerequisites**

1. Python 3.8+
2. Required Python libraries (see `requirements.txt`):
   - `discord.py`
   - `loguru`
   - `dotenv`
3. A `.env` file with the following variables:

   ```env
   BOT_TOKEN=your-discord-bot-token
   GUILD_ID=your-guild-id
   ```

### **Deployment**

1. Clone this repository:

   ```bash
   git clone https://github.com/your-repo/kasutamaiza-bot.git
   cd kasutamaiza-bot
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your `.env` file with your bot token and guild ID.

4. Run the bot:

   ```bash
   python main.py
   ```

---

## **Commands**

### **Core Commands**

- `/ping`: Check if the bot is online and view latency.
- `/help`: Display the help message with categorized commands.
- `/uptime`: View how long the bot has been running.

### **Diagnostics**

- `/diagnostics`: View detailed diagnostics including:
  - Bot uptime, permissions, loaded cogs, and environment variables.

### **Moderation Commands**

- `/kick [member] [reason]`: Kick a member from the server.
- `/ban [member] [reason]`: Ban a member from the server.
- `/mute [member] [duration] [reason]`: Temporarily mute a member.
- `/unmute [member]`: Unmute a member.
- `/purge [amount]`: Delete multiple messages.
- `/warn [member] [reason]`: Issue a warning to a member.

### **Yu-Gi-Oh Specific**

- `/dueling`: Get a link to DuelingBook for online dueling.
- `/card_lookup [query]`: Search for a Yu-Gi-Oh! card by name, type, or filters.
- `/deck_tips`: Get general tips for building a Yu-Gi-Oh! deck.
- `/tournament_links`: Get links to Yu-Gi-Oh tournaments and events.

---

## **Cogs**

### **Current Cogs**

1. **Debug**:
   - Diagnostics and permission checks.
   - `/diagnostics`, `/check_permissions`.

2. **General**:
   - General-purpose commands like `/ping`, `/help`, `/uptime`.

3. **Moderation**:
   - Moderation tools like `/kick`, `/ban`, `/mute`, and `/warn`.

4. **Utility**:
   - Server-related utilities like `/info`, `/server_info`.

5. **Yu-Gi-Oh**:
   - Specialized commands for Yu-Gi-Oh players (`/dueling`, `/card_lookup`).

---

## **Technical Details**

### **Architecture**

- **Cog-Based Design**:
  - Each feature set is implemented in separate cogs (`Debug`, `General`, `Moderation`, etc.).
  - Cogs are dynamically loaded at runtime for flexibility and modularity.

- **Permissions Management**:
  - The bot validates required permissions (`Administrator`, `Manage Roles`, etc.) on startup.
  - Missing permissions are logged for easy debugging.

- **Error Handling**:
  - Commands gracefully handle errors with informative messages.
  - Logs capture all errors and warnings.

- **Heartbeat**:
  - Periodic logs confirm the bot is online and operational.

---

## **Roadmap**

### **Step 2 of Phase 1**

- Persistent data storage using a database (e.g., PostgreSQL) for:
  - Moderation logs (`/warn`, `/mute`).
  - Custom configurations for guilds.
- Expanded APIs for enhanced features (`/card_lookup` with caching).

### **Future Phases**

- Event scheduling for community engagement.
- Advanced Yu-Gi-Oh utilities (e.g., deck analysis, synergy detection).

---

## **Contributing**

Feel free to contribute by opening issues or submitting pull requests. Ensure all changes are tested and documented.

---

## **License**

This project is licensed under the [MIT License](LICENSE).
