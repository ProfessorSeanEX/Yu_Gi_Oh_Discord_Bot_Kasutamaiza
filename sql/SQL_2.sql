CREATE TABLE bot_users (
    id SERIAL PRIMARY KEY,
    discord_id BIGINT NOT NULL UNIQUE,
    username VARCHAR(100),
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_banned BOOLEAN DEFAULT FALSE
);

CREATE TABLE guild_settings (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    setting_key VARCHAR(50) NOT NULL,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE command_logs (
    id SERIAL PRIMARY KEY,
    guild_id BIGINT,
    user_id BIGINT NOT NULL,
    command VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE moderation_logs (
    id SERIAL PRIMARY KEY,
    moderator_id BIGINT NOT NULL,
    target_user_id BIGINT NOT NULL,
    action VARCHAR(50),
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
