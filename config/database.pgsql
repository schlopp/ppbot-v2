DROP SCHEMA public CASCADE;
CREATE SCHEMA public;


CREATE TABLE IF NOT EXISTS guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30)
);


CREATE TABLE IF NOT EXISTS user_settings(
    user_id BIGINT PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS items(
    name text PRIMARY KEY,
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
    lore text[]
);


CREATE TABLE IF NOT EXISTS user_inventory(
    user_id BIGINT NOT NULL,
    name text NOT NULL,
    amount INT NOT NULL,
    PRIMARY KEY (user_id, name)
);


CREATE TABLE IF NOT EXISTS user_skill(
    user_id BIGINT NOT NULL,
    name text NOT NULL,
    level INT NOT NULL,
    experience BIGINT NOT NULL,
    PRIMARY KEY (user_id, name)
);


CREATE TABLE IF NOT EXISTS user_pp(
    user_id BIGINT PRIMARY KEY,
    name text DEFAULT 'Unnamed pp' NOT NULL,
    amount BIGINT NOT NULL,
    multiplier FLOAT DEFAULT 1.0 NOT NULL
);