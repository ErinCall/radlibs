(function () {
	'use strict';
	var new_lib,
		test_radlib,
		save_all,
		radlibs = window.radlibs;

	new_lib = function() {
		document.location = $( 'body' ).data( 'new_lib_url' );
	};

	test_radlib = function( event ) {
		event.preventDefault();
		var rad,
			test_radlib_url;

		rad = $( '#radlib' ).val();
		test_radlib_url = $( 'body' ).data( 'test_radlib_url' );
		$.ajax( test_radlib_url, {
			type: 'POST',
			data: { rad: rad },
			success: function(data, status, jqXHR) {
				var body = JSON.parse( data );
				if( body[ 'status' ] === 'ok' ) {
					radlibs.display_radlib( body[ 'radlib' ] );
				} else {
					radlibs.display_error( body[ 'error' ] );
				}
			},
			error: function(jqXHR, status, errorThrown) {
				alert( errorThrown );
			}
		});
	};

	$(document).ready(function() {
		radlibs.draw_new_lib_button(new_lib);
		$( '#fire' ).click( test_radlib );
		$( '#radlib-form' ).submit( test_radlib );
	});
})();