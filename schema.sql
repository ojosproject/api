CREATE TABLE IF NOT EXISTS tokens (
    token TEXT UNIQUE PRIMARY KEY,
    expiration_date NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS token_log (
    id SERIAL PRIMARY KEY,
    token TEXT REFERENCES tokens(token),
    timestamp NUMERIC,
    message_type TEXT -- SMS, email, etc
    -- count NUMERIC
);
/* 
SERIAL is an integer type that is automatically assigned and automatically
increments, making it perfect to serve as a primary key. 

It is automatically assigned, so inserting into token_log only requires values
for token and timestamp, meaning
INSERT INTO token_log (token, timestamp, message_type) VALUES ("a", 0, "SMS")
is valid
*/

