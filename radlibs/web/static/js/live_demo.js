(function() {
	'use strict';

	var fire,
		collect_libs,
		display_radlib,
		display_error;

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
				var body = JSON.parse( data );

				if ( body[ 'status' ] === 'ok' ) {
					display_radlib( body[ 'radlib' ] );
				} else {
					display_error( body[ 'error' ] );
				}
			},
			error: function(jqXHR, status, errorThrown) {
				alert( errorThrown );
			}
		});
	};

	display_radlib = function(radlib) {
		var $jumbotron,
			$h1,
			$error;

		$jumbotron = $( '.jumbotron' );
		$h1 = $jumbotron.find( 'h1' );
		$error = $jumbotron.find( 'h4' );
		$error.remove();

		if ( $h1.length === 0 ) {
			$h1 = $( '<h1>' );
			$jumbotron.prepend( $h1 );
		}

		$h1.text( radlib );
	};

	display_error = function( error ) {
		var $jumbotron,
			$h1,
			$error;

		$jumbotron = $( '.jumbotron' );
		$h1 = $jumbotron.find( 'h1' );
		$error = $jumbotron.find( 'h4' );
		$h1.remove();

		if ( $error.length === 0 ) {
			$error = $( '<h4>' );
			$error.attr('class', 'error');
			$jumbotron.prepend( $error );
		}

		$error.text( error );
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