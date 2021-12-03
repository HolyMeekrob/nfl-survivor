(function () {
	let handlePageLoad;

	const getSeasonId = () => parseInt(document.getElementById('season-id').value, 10);

	const getUpdateGamesForm = () => document.getElementById('update-games');
	const getUpdateRulesForm = () => document.getElementById('update-rules');
	const getInviteNewUserForm = () => document.getElementById('invite-new-user');
	const getInviteButtons = () => document.querySelectorAll('[data-action="invite"]');

	const updateFromServer = (request) => {
		fetch(request)
			.then((response) => response.text())
			.then((page) => {
				document.open('text/html', 'replace');
				document.write(page);
				document.close();
			});
	};

	const updateGames = (e) => {
		e.preventDefault();

		const form = getUpdateGamesForm();
		const data = new FormData(form);
		const request = new Request(form.action, {
			method: form.method,
			body: data,
		});

		updateFromServer(request);
	};

	const updateRules = (e) => {
		e.preventDefault();

		const form = getUpdateRulesForm();
		const data = new FormData(form);
		const request = new Request(form.action, {
			method: form.method,
			body: data,
		});

		updateFromServer(request);
	};

	const inviteNewUser = (e) => {
		e.preventDefault();

		const form = getInviteNewUserForm();
		const data = new FormData(form);
		const request = new Request(form.action, {
			method: form.method,
			body: data,
		});

		updateFromServer(request);
	};

	const sendInvite = (e) => {
		const userId = e.target.dataset.id;

		const request = new Request('inviteUser', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				seasonId: getSeasonId(),
				userId: userId,
			}),
		});

		updateFromServer(request);
	};

	handlePageLoad = () => {
		const updateGamesForm = getUpdateGamesForm();
		updateGamesForm.addEventListener('submit', updateGames);

		const updateRulesForm = getUpdateRulesForm();
		if (updateRulesForm) {
			updateRulesForm.addEventListener('submit', updateRules);
		}

		const inviteNewUserForm = getInviteNewUserForm();
		if (inviteNewUserForm) {
			inviteNewUserForm.addEventListener('submit', inviteNewUser);
		}

		for (const button of getInviteButtons()) {
			button.addEventListener('click', sendInvite);
		}
	};

	window.addEventListener('load', handlePageLoad);
})();
