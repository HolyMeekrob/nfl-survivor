PRAGMA foreign_keys=OFF;

BEGIN TRANSACTION;

CREATE TABLE user_new (
	id UUID PRIMARY KEY,
	email TEXT NOT NULL UNIQUE DEFAULT '',
	first_name TEXT,
	last_name TEXT,
	nickname TEXT,
	password TEXT NOT NULL
);


INSERT INTO user_new SELECT id, email, first_name, last_name, nickname, password FROM user;

DROP TABLE user;

ALTER TABLE user_new RENAME TO user;

CREATE TABLE season_participant_new (
	season_id INTEGER NOT NULL,
	user_id UUID NOT NULL,

	PRIMARY KEY(season_id, user_id),
	FOREIGN KEY(season_id) REFERENCES season(id),
	FOREIGN KEY(user_id) REFERENCES user(id)
);

INSERT INTO season_participant_new SELECT season_id, user_id FROM season_participant;

DROP TABLE season_participant;

ALTER TABLE season_participant_new RENAME TO season_participant;

COMMIT TRANSACTION;

PRAGMA foreign_keys=ON;