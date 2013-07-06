(function () {
	'use strict';
	var new_lib,
		save_all,
		radlibs = window.radlibs;

	new_lib = function() {
		document.location = $( 'body' ).data( 'new_lib_url' );
	};

	$(document).ready(function() {
		radlibs.draw_new_lib_button(new_lib);
	});
})();