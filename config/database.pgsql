CREATE TABLE IF NOT EXISTS guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix TEXT
);


CREATE TABLE IF NOT EXISTS user_settings(
    user_id BIGINT PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS role_list(
    guild_id BIGINT,
    role_id BIGINT,
    key TEXT,
    value TEXT,
    PRIMARY KEY (guild_id, role_id, key)
);


CREATE TABLE IF NOT EXISTS channel_list(
    guild_id BIGINT,
    channel_id BIGINT,
    key TEXT,
    value TEXT,
    PRIMARY KEY (guild_id, channel_id, key)
);


CREATE TABLE IF NOT EXISTS user_pp(
    user_id BIGINT PRIMARY KEY,
    name TEXT DEFAULT 'Unnamed pp' NOT NULL,
    size BIGINT NOT NULL,
    multiplier FLOAT DEFAULT 1.0 NOT NULL
);


CREATE TABLE IF NOT EXISTS user_skill(
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    experience BIGINT DEFAULT 0 NOT NULL,
    PRIMARY KEY (user_id, name)
);


CREATE TABLE IF NOT EXISTS user_inv(
    user_id BIGINT NOT NULL,
    item_id TEXT NOT NULL,
    amount INT NOT NULL,
)
