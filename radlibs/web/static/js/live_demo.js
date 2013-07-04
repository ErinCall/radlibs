(function() {
	'use strict';

	var submit_radlib,
		collect_libs,
		draw_new_lib_button,
		add_new_lib,
		row_with_vacancy,
		display_radlib,
		display_error;

	submit_radlib = function( event ) {
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

	draw_new_lib_button = function() {
		var $button;

		$button = $( '<div>' );
		$button.addClass( 'span4' );
		$button.attr( 'id', 'new-lib-button' );
		$button.css( 'font-size', '100px' );
		$button.css( 'text-align', 'center' );
		$button.css( 'border', 'dashed 1px');
		$button.css( 'margin-top', '40px' );
		$button.css( 'padding-top', '90px' );
		$button.css( 'padding-bottom', '110px' );
		$button.text( '+' );
		$button.click( add_new_lib );
		row_with_vacancy().append( $button );
	};

	add_new_lib = function () {
		var $new_lib_button,
			lib_name,
			uc_lib_name,
			$textarea,
			$header,
			$div;

		lib_name = prompt('name your new lib:');
		uc_lib_name = lib_name.charAt( 0 ).toUpperCase() + lib_name.slice( 1 );

		$new_lib_button = $( '#new-lib-button' );
		$new_lib_button.detach();

		$div = $( '<div>' );
		$div.addClass( 'span4' );

		$textarea = $( '<textarea>' );
		$textarea.addClass( 'library' );
		$textarea.attr( 'rows', '10' );
		$textarea.attr( 'name', lib_name );
		$textarea.attr( 'id', lib_name );

		$header = $( '<h4>' );
		$header.text( uc_lib_name );

		$div.append( $header );
		$div.append( $textarea );

		row_with_vacancy().append( $div );
		row_with_vacancy().append( $new_lib_button );
	};

	row_with_vacancy = function (){
		var $last_row,
			entries_in_row,
			$new_row;

		$last_row = $( 'div.row-fluid' ).last();
		entries_in_row = $last_row.find( 'div.span4' ).length;
		if ( entries_in_row >= 3 ) {
			$new_row = $( '<div>' );
			$new_row.addClass( 'row-fluid marketing' );
			$( '#page-content' ).append( $new_row );
			return $new_row;
		} else {
			return $last_row;
		}
	};

	$(document).ready(function() {
		$( '#radlib-form' ).submit(submit_radlib);
		$( '#fire' ).click(submit_radlib);
		$( '#radlib' ).focus().select();
		draw_new_lib_button();
	});
})();