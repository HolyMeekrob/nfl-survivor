CREATE TABLE rules(
	id INTEGER PRIMARY KEY,
	max_strikes INTEGER NOT NULL CHECK(max_strikes > 0),
	max_team_picks INTEGER NOT NULL CHECK(max_team_picks > 0),
	pick_cutoff WEEK_TIMER NOT NULL,
	pick_reveal WEEK_TIMER NOT NULL,
	entry_fee REAL NOT NULL CHECK(entry_fee >= 0),
	winnings REAL_ARRAY NOT NULL CHECK(winnings >= 0),

	FOREIGN KEY(id) REFERENCES season(id)
);