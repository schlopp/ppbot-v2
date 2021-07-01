CREATE TABLE IF NOT EXISTS guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30)
);


CREATE TABLE IF NOT EXISTS user_settings(
    user_id BIGINT PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS items(
    name TEXT PRIMARY KEY,
    requires JSONB DEFAULT '{}',
    type TEXT NOT NULL,
    rarity TEXT NOT NULL,
    auctionable boolean DEFAULT False,
    description text NOT NULL,
    emoji BIGINT NOT NULL,
    used_for TEXT[] DEFAULT '{}',
    recipe JSONB DEFAULT '{}',
    recipes JSONB DEFAULT '{}',
    buffs JSONB[] DEFAULT '{}',
    shop_for_sale BOOL NOT NULL,
    shop_buy INT NOT NULL,
    shop_sell INT NOT NULL,
    story TEXT[] DEFAULT '{}'
);


CREATE TABLE IF NOT EXISTS user_inventory(
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    amount INT NOT NULL,
    PRIMARY KEY (user_id, name)
);


CREATE TABLE IF NOT EXISTS user_skill(
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    level INT NOT NULL,
    experience BIGINT NOT NULL,
    PRIMARY KEY (user_id, name)
);


CREATE TABLE IF NOT EXISTS user_pp(
    user_id BIGINT PRIMARY KEY,
    name TEXT DEFAULT 'Unnamed pp' NOT NULL,
    amount BIGINT NOT NULL,
    multiplier FLOAT DEFAULT 1.0 NOT NULL
);
