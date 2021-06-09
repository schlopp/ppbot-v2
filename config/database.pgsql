CREATE TABLE IF NOT EXISTS guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30)
);


CREATE TABLE IF NOT EXISTS user_settings(
    user_id BIGINT PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS role_list(
    guild_id BIGINT,
    role_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, role_id, key)
);


CREATE TABLE IF NOT EXISTS channel_list(
    guild_id BIGINT,
    channel_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, channel_id, key)
);


CREATE TABLE IF NOT EXISTS items(
    name text NOT NULL,
    id bigint NOT NULL,
    for_sale boolean,
    requires json,
    type text NOT NULL,
    rarity text NOT NULL,
    buy integer,
    sell integer,
    auctionable boolean,
    description text NOT NULL,
    emoji text NOT NULL,
    recipe json,
    usage json,
    recipes json,
    buffs json,
    lore text[],
    PRIMARY KEY (id)
);