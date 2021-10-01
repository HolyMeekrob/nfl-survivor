CREATE TABLE team (
	id INTEGER PRIMARY KEY,
	location TEXT,
	name TEXT UNIQUE,
	abbreviation TEXT UNIQUE
);

CREATE TABLE season_type(
	id INTEGER PRIMARY KEY,
	name TEXT
);

CREATE TABLE season(
	id INTEGER PRIMARY KEY,
	season_type INTEGER NOT NULL,
	year INTEGER NOT NULL,

	FOREIGN KEY(season_type) REFERENCES season_type(id)
);

CREATE TABLE week(
	id INTEGER PRIMARY KEY,
	season_id INTEGER NOT NULL,
	number INTEGER NOT NULL CHECK(number >= 0),

	FOREIGN KEY(season_id) REFERENCES season(id)
);

CREATE TABLE game (
	id INTEGER PRIMARY KEY,
	week_id INTEGER NOT NULL,
	away_team_id INTEGER NOT NULL CHECK(away_team_id != home_team_id),
	home_team_id INTEGER NOT NULL CHECK(home_team_id != away_team_id),
	away_score INTEGER NOT NULL DEFAULT 0 CHECK(away_score >= 0),
	home_score INTEGER NOT NULL DEFAULT 0 CHECK(home_score >= 0),
	odds REAL,
	kickoff TEXT,

	FOREIGN KEY(week_id) REFERENCES week(id)
	FOREIGN KEY(away_team_id) REFERENCES team(id),
	FOREIGN KEY(home_team_id) REFERENCES team(id)
);

CREATE TABLE migration (
	id INTEGER PRIMARY KEY,
	version INTEGER NOT NULL,
	timestamp TEXT NOT NULL
)