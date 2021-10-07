ALTER TABLE season
ADD COLUMN name TEXT NOT NULL DEFAULT '';

CREATE TABLE user(
	id BLOB PRIMARY KEY,
	email TEXT NOT NULL DEFAULT '',
	first_name TEXT,
	last_name TEXT,
	nickname TEXT
);

CREATE TABLE season_participant(
	season_id INTEGER NOT NULL,
	user_id BLOB NOT NULL,

	PRIMARY KEY(season_id, user_id),
	FOREIGN KEY(season_id) REFERENCES season(id),
	FOREIGN KEY(user_id) REFERENCES user(id)
);
