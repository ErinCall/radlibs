(function () {
	'use strict';
	var show_signin_widget;

	show_signin_widget = function(event) {
		event.preventDefault();
		$( '#janrainEngageEmbed' ).toggle();
	};

	$(document).ready(function () {
		$( '#show-sign-in' ).click( show_signin_widget );
	});
})();