CREATE TABLE pick(
	week_id INTEGER NOT NULL,
	user_id UUID NOT NULL,
	team_id INTEGER NOT NULL,

	PRIMARY KEY(week_id, user_id),
	FOREIGN KEY(week_id) REFERENCES week(id),
	FOREIGN KEY(user_id) REFERENCES user(id),
	FOREIGN KEY(team_id) REFERENCES team(id)
);