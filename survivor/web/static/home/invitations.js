(function () {
	const getAcceptButtons = () => document.querySelectorAll('[data-action="accept"]');
	const getDeclineButtons = () => document.querySelectorAll('[data-action="decline"]');

	const getSeasonId = (elem) => parseInt(elem.closest('[data-season-id').dataset.seasonId, 10);

	const updateFromServer = (request) => {
		fetch(request)
			.then((response) => response.text())
			.then((page) => {
				document.open('text/html', 'replace');
				document.write(page);
				document.close();
			});
	};

	const acceptInvitation = (e) => {
		seasonId = getSeasonId(e.target);

		const request = new Request(`acceptInvitation/${seasonId}`, {
			method: 'POST',
		});

		updateFromServer(request);
	};

	const declineInvitation = (e) => {
		seasonId = getSeasonId(e.target);

		const request = new Request(`declineInvitation/${seasonId}`, {
			method: 'POST',
		});

		updateFromServer(request);
	};

	const addAcceptListeners = () => {
		const buttons = getAcceptButtons();
		for (const button of buttons) {
			button.addEventListener('click', acceptInvitation);
		}
	};

	const addDeclineListeners = () => {
		const buttons = getDeclineButtons();
		for (const button of buttons) {
			button.addEventListener('click', declineInvitation);
		}
	};

	const handlePageLoad = () => {
		addAcceptListeners();
		addDeclineListeners();
	};

	window.addEventListener('load', handlePageLoad);
})();
