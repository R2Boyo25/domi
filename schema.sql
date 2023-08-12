CREATE TABLE users (
    gpg_pubkey VARBINARY(512000000),
    profile_picture VARCHAR(2000), -- A URL
    user_snowflake BINARY(8)
);

CREATE TABLE sessions (
    user_snowflake BINARY(8),
    session_token BINARY(2048),
    ip_address,
    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages(
    message_id BINARY(8),
    thread_id BINARY(8),
    author_id BINARY(8),
    content VARBINARY(512000000)
);

CREATE TABLE threads(
    thread_snowflake BINARY(8),
    parent_snowflake BINARY(8)
    thread_name VARCHAR(32),
    recipients VARBINARY(8000000) -- List of user_snowflakes or empty for public
);
