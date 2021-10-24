CREATE TABLE season_invitation(
	season_id INTEGER NOT NULL,
	user_id UUID NOT NULL,
	status INVITATION_STATUS NOT NULL DEFAULT 'PENDING',

	PRIMARY KEY(season_id, user_id),
	FOREIGN KEY(season_id) REFERENCES season(id),
	FOREIGN KEY(user_id) REFERENCES user(id)
);