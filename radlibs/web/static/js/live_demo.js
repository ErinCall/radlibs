(function() {
	'use strict';

	var fire,
		collect_libs;

	fire = function( event ) {
		event.preventDefault();
		var rad,
			libs = collect_libs();

		rad = $( '#radlib' ).val();

		$.ajax( '/demo_eval', {
			type: "POST",
			data: {
				libs: JSON.stringify(libs),
				rad: rad
			},
			success: function(data, status, jqXHR) {
				var $jumbotron,
					$h1;

				$jumbotron = $( '.jumbotron' );
				$h1 = $jumbotron.find( 'h1' );

				if ( $h1.length === 0 ) {
					$h1 = $( '<h1>' );
					$jumbotron.prepend( $h1 );
				}

				$h1.text( JSON.parse( data )[ 'radlib' ] );
			},
			error: function(jqXHR, status, errorThrown) {
				alert( errorThrown );
			}
		});
	};

	collect_libs = function() {
		var libs = {};

		_.each( $( '.library' ), function( textarea ) {
			var $textarea,
				lib_name,
				uc_lib_name,
				lines;

			$textarea = $(textarea);
			lib_name = $textarea.attr( 'name' );
			uc_lib_name = lib_name.charAt(0).toUpperCase() + lib_name.slice( 1 );
			lines = $textarea.val().split( "\n" );

			libs[uc_lib_name] = lines;
		});

		return libs;
	};

	$(document).ready(function() {
		$( '#radlib-form' ).submit(fire);
		$( '#fire' ).click(fire);
		$( '#radlib' ).focus().select();
	});
})();