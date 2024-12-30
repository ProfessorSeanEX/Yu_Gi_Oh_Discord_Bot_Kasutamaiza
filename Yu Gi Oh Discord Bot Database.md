# **Yu-Gi-Oh! Bot Database Plan**

This document outlines the comprehensive database schema to support all features of the Yu-Gi-Oh! bot, incorporating elements from all eight pieces and additional requirements derived from the card lookup code.

---

## **1. Core User Management**

### **`bot_users`**

- **Purpose**: Tracks users interacting with the bot.
- **Columns**:
  - `user_id` (BigInt, Primary Key): Discord user ID.
  - `username` (Text): Discord username.
  - `join_date` (Timestamp): Join date.
  - `elo_rating` (Integer): Competitive ranking.
  - `is_admin` (Boolean): Admin status.

### **`user_profiles`**

- **Purpose**: Extended user information.
- **Columns**:
  - `user_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `bio` (Text): Custom player bio.
  - `avatar_url` (Text): Avatar image URL.
  - `preferences` (JSON): Custom settings (theme, notifications).

---

## **2. Card System**

### **`card_library`**

- **Purpose**: Master list of all cards.
- **Columns**:
  - `card_id` (Serial, Primary Key): Unique card ID.
  - `name` (Text): Card name.
  - `description` (Text): Card description.
  - `type` (Text): Monster, Spell, or Trap.
  - `rarity` (Text): Rarity level.
  - `attack` (Integer): Attack points.
  - `defense` (Integer): Defense points.
  - `image_url` (Text): Artwork URL.
  - `pendulum_scale` (Integer): Pendulum scale (if applicable).
  - `pendulum_effect` (Text): Pendulum-specific effects.
  - `link_rating` (Integer): Link monster rating (if applicable).
  - `link_markers` (JSONB): Link marker positions.
  - `search_metadata` (TSVECTOR): Precomputed searchable data.

### **`card_variants`**

- **Purpose**: Stores multiple versions of a card.
- **Columns**:
  - `variant_id` (Serial, Primary Key): Unique variant ID.
  - `card_id` (BigInt, Foreign Key): References `card_library.card_id`.
  - `set_code` (Text): Set or edition code.
  - `effect_text` (Text): Variant-specific effects.
  - `image_url` (Text): Variant artwork URL.

### **`player_collections`**

- **Purpose**: Tracks cards owned by players.
- **Columns**:
  - `collection_id` (Serial, Primary Key): Unique collection ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `card_id` (BigInt, Foreign Key): References `card_library.card_id`.
  - `quantity` (Integer): Number of cards owned.

### **`deck_builder`**

- **Purpose**: Stores player decks.
- **Columns**:
  - `deck_id` (Serial, Primary Key): Unique deck ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `name` (Text): Deck name.
  - `card_list` (JSON): JSON array of card IDs.

---

## **3. Economy**

### **`player_wallets`**

- **Purpose**: Tracks player currency balances.
- **Columns**:
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `balance` (Numeric): Total balance.

### **`transaction_logs`**

- **Purpose**: Logs financial transactions.
- **Columns**:
  - `transaction_id` (Serial, Primary Key): Unique transaction ID.
  - `player_id` (BigInt, Foreign Key): References `player_wallets.player_id`.
  - `amount` (Numeric): Amount spent or earned.
  - `description` (Text): Transaction details.
  - `timestamp` (Timestamp): Date and time.

### **`currency_fluctuations`**

- **Purpose**: Tracks trends in in-game currency.
- **Columns**:
  - `fluctuation_id` (Serial, Primary Key): Unique fluctuation ID.
  - `timestamp` (Timestamp): Date of the fluctuation.
  - `supply` (Numeric): Current currency supply.
  - `demand` (Numeric): Current currency demand.

### **`item_value_history`**

- **Purpose**: Tracks historical prices of items/cards.
- **Columns**:
  - `value_id` (Serial, Primary Key): Unique value record ID.
  - `card_id` (BigInt, Foreign Key): References `card_library.card_id`.
  - `price` (Numeric): Historical price.
  - `timestamp` (Timestamp): Date of the price entry.

---

## **4. Marketplace**

### **`card_marketplace`**

- **Purpose**: Tracks card listings.
- **Columns**:
  - `listing_id` (Serial, Primary Key): Unique listing ID.
  - `seller_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `card_id` (BigInt, Foreign Key): References `card_library.card_id`.
  - `price` (Numeric): Sale price.
  - `status` (Text): Listing status (`available`, `sold`, `removed`).

### **`card_transactions`**

- **Purpose**: Logs completed marketplace transactions.
- **Columns**:
  - `transaction_id` (Serial, Primary Key): Unique transaction ID.
  - `buyer_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `seller_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `card_id` (BigInt, Foreign Key): References `card_library.card_id`.
  - `price` (Numeric): Sale price.
  - `timestamp` (Timestamp): Transaction date.

---

## **5. Dueling System**

### **`duel_sessions`**

- **Purpose**: Logs duels.
- **Columns**:
  - `session_id` (Serial, Primary Key): Unique duel session ID.
  - `player_1_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `player_2_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `status` (Text): Duel status (`active`, `completed`, `abandoned`).
  - `winner_id` (BigInt, Foreign Key): Winner ID.
  - `log_data` (JSON): Turn-by-turn log.

### **`duel_results`**

- **Purpose**: Tracks duel outcomes.
- **Columns**:
  - `result_id` (Serial, Primary Key): Unique result ID.
  - `session_id` (BigInt, Foreign Key): References `duel_sessions.session_id`.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `result` (Text): Win, loss, or draw.
  - `rating_change` (Integer): ELO adjustment.

---

## **6. Custom Formats**

### **`formats`**

- **Purpose**: Stores custom gameplay formats.
- **Columns**:
  - `format_id` (Serial, Primary Key): Unique format ID.
  - `name` (Text): Format name.
  - `description` (Text): Format description.
  - `rules` (JSON): JSON object defining rules.

### **`banlists`**

- **Purpose**: Tracks banned or restricted cards for each format.
- **Columns**:
  - `banlist_id` (Serial, Primary Key): Unique banlist ID.
  - `format_id` (BigInt, Foreign Key): References `formats.format_id`.
  - `card_id` (BigInt, Foreign Key): References `card_library.card_id`.
  - `restriction` (Text): Restriction level (`banned`, `limited`, `semi-limited`).

---

## **7. Card Lore**

### **`card_lore`**

- **Purpose**: Tracks lore for individual cards.
- **Columns**:
  - `lore_id` (Serial, Primary Key): Unique lore entry ID.
  - `card_id` (BigInt, Foreign Key): References `card_library.card_id`.
  - `story` (Text): Lore description.

### **`archetypes`**

- **Purpose**: Tracks archetype themes and associated cards.
- **Columns**:
  - `archetype_id` (Serial, Primary Key): Unique archetype ID.
  - `name` (Text): Archetype name.
  - `description` (Text): Archetype lore.

### **`lore_events`**

- **Purpose**: Tracks player-driven lore changes.
- **Columns**:
  - `event_id` (Serial, Primary Key): Unique event ID.
  - `description` (Text): Event description.
  - `timestamp` (Timestamp): Event date.
  - `outcome` (JSON): JSON object defining lore changes.

---

## **8. Story Mode**

### **`story_progress`**

- **Purpose**: Tracks player progress in story mode.
- **Columns**:
  - `progress_id` (Serial, Primary Key): Unique progress ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `chapter` (Integer): Current chapter.
  - `completion_status` (Text): Progress within the chapter.
  - `last_updated` (Timestamp): Progress update time.

### **`story_nodes`**

- **Purpose**: Tracks branching narratives.
- **Columns**:
  - `node_id` (Serial, Primary Key): Unique narrative node ID.
  - `chapter` (Integer): Associated story chapter.
  - `description` (Text): Narrative description.
  - `options` (JSON): JSON object defining branching choices.

---

## **9. Community Features**

### **`clans`**

- **Purpose**: Tracks clan information.
- **Columns**:
  - `clan_id` (Serial, Primary Key): Unique clan ID.
  - `name` (Text): Clan name.
  - `description` (Text): Clan description.

### **`clan_members`**

- **Purpose**: Tracks clan memberships.
- **Columns**:
  - `membership_id` (Serial, Primary Key): Unique membership ID.
  - `clan_id` (BigInt, Foreign Key): References `clans.clan_id`.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.

---

## **10. Gamification**

### **`daily_rewards`**

- **Purpose**: Tracks daily player rewards.
- **Columns**:
  - `reward_id` (Serial, Primary Key): Unique reward ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `reward_claimed` (Boolean): Whether the reward was claimed.
  - `timestamp` (Timestamp): Claim date.

### **`level_progress`**

- **Purpose**: Tracks player leveling and XP.
- **Columns**:
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `current_level` (Integer): Current level.
  - `current_xp` (Integer): Current XP.

---

## **11. Advanced Analytics**

### **`format_statistics`**

- **Purpose**: Logs format popularity and balance.
- **Columns**:
  - `stat_id` (Serial, Primary Key): Unique stat ID.
  - `format_id` (BigInt, Foreign Key): References `formats.format_id`.
  - `win_count` (Integer): Number of wins in this format.
  - `loss_count` (Integer): Number of losses in this format.
  - `last_updated` (Timestamp): Last update time.

---

### **12. AI Features**

#### **`ai_training_data`**

- **Purpose**: Stores patterns for improving bot AI behavior.
- **Columns**:
  - `data_id` (Serial, Primary Key): Unique data ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `action_log` (JSON): Logs AI decisions and moves.
  - `feedback` (Text): Player feedback on AI performance.

#### **`ai_model_versions`**

- **Purpose**: Tracks updates to AI models.
- **Columns**:
  - `version_id` (Serial, Primary Key): Unique version ID.
  - `release_date` (Timestamp): Release date of the AI model.
  - `description` (Text): Details of the update.
  - `win_rate` (Numeric): AI’s win rate in testing.

#### **`ai_profiles`**

- **Purpose**: Stores AI personalization data.
- **Columns**:
  - `profile_id` (Serial, Primary Key): Unique profile ID.
  - `name` (Text): Name of the AI personality.
  - `difficulty` (Text): AI difficulty level (e.g., Easy, Hard).
  - `customization` (JSON): Configuration settings for this profile.

#### **`ai_training_sessions`**

- **Purpose**: Tracks AI training data from player interactions.
- **Columns**:
  - `session_id` (Serial, Primary Key): Unique session ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `training_data` (JSON): Details of the training session.
  - `feedback` (Text): Player feedback after training.

---

### **13. Scalability**

#### **`session_cache`**

- **Purpose**: Temporarily caches active sessions for scalability.
- **Columns**:
  - `session_id` (BigInt, Primary Key): Session ID.
  - `data` (JSON): Cached session data.
  - `expiry` (Timestamp): Expiration date and time.

#### **`rate_limit_logs`**

- **Purpose**: Logs rate-limiting activity for bot API usage.
- **Columns**:
  - `log_id` (Serial, Primary Key): Unique log ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `endpoint` (Text): API endpoint accessed.
  - `timestamp` (Timestamp): Access time.

---

### **14. Real-World TCG Integration**

#### **`scanned_cards`**

- **Purpose**: Tracks scanned physical cards for virtual collection integration.
- **Columns**:
  - `scan_id` (Serial, Primary Key): Unique scan ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `card_data` (JSON): Data of the scanned card.
  - `timestamp` (Timestamp): Time of the scan.

---

### **15. Advanced Analytics**

#### **`format_statistics`**

- **Purpose**: Logs win/loss data for formats to track popularity and balance.
- **Columns**:
  - `stat_id` (Serial, Primary Key): Unique stat ID.
  - `format_id` (BigInt, Foreign Key): References `formats.format_id`.
  - `win_count` (Integer): Number of wins in this format.
  - `loss_count` (Integer): Number of losses in this format.
  - `last_updated` (Timestamp): Last update time.

#### **`match_analytics`**

- **Purpose**: Provides detailed analysis of matches.
- **Columns**:
  - `analytics_id` (Serial, Primary Key): Unique match analytics ID.
  - `session_id` (BigInt, Foreign Key): References `duel_sessions.session_id`.
  - `turn_count` (Integer): Total number of turns.
  - `average_turn_time` (Numeric): Average time per turn in seconds.
  - `most_used_card` (Text): Most frequently played card.

---

### **16. Gamification**

#### **`daily_rewards`**

- **Purpose**: Tracks daily rewards for players.
- **Columns**:
  - `reward_id` (Serial, Primary Key): Unique reward ID.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `reward_claimed` (Boolean): Whether the reward was claimed.
  - `timestamp` (Timestamp): Claim date and time.

#### **`level_progress`**

- **Purpose**: Tracks player leveling and experience points (XP).
- **Columns**:
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.
  - `current_level` (Integer): Player’s current level.
  - `current_xp` (Integer): Experience points towards the next level.

---

### **17. Community Engagement**

#### **`clans`**

- **Purpose**: Stores clan or team information.
- **Columns**:
  - `clan_id` (Serial, Primary Key): Unique clan ID.
  - `name` (Text): Name of the clan.
  - `description` (Text): Description of the clan.
  - `created_at` (Timestamp): When the clan was formed.

#### **`clan_members`**

- **Purpose**: Tracks membership in clans or teams.
- **Columns**:
  - `membership_id` (Serial, Primary Key): Unique membership ID.
  - `clan_id` (BigInt, Foreign Key): References `clans.clan_id`.
  - `player_id` (BigInt, Foreign Key): References `bot_users.user_id`.

---

### **18. Experimental Gameplay Features**

#### **`chaos_rules`**

- **Purpose**: Tracks randomized mechanics for Chaos Format.\n- **Columns**:
  - `rule_id` (Serial, Primary Key): Unique rule ID.
  - `description` (Text): Description of the rule.
  - `active` (Boolean): Whether the rule is currently in effect.

#### **`draft_pools`**

- **Purpose**: Manages card pools for Draft Mode.\n- **Columns**:
  - `pool_id` (Serial, Primary Key): Unique pool ID.
  - `cards` (JSON): JSON array of card IDs in the pool.
  - `created_at` (Timestamp): When the pool was created.

---
