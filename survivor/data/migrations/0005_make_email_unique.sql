PRAGMA foreign_keys=OFF;

BEGIN TRANSACTION;

CREATE TABLE user_new(
	id BLOB PRIMARY KEY,
	email TEXT NOT NULL UNIQUE DEFAULT '',
	first_name TEXT,
	last_name TEXT,
	nickname TEXT
);

INSERT INTO user_new SELECT id, email, first_name, last_name, nickname FROM user;

DROP TABLE user;

ALTER TABLE user_new RENAME TO user;

COMMIT TRANSACTION;

PRAGMA foreign_keys=ON;