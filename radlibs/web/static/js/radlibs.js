(function () {
	'use strict';
	var show_signin_widget;
	if (typeof window.radlibs === "undefined" ) {
		window.radlibs = {};
	}

	window.radlibs.row_with_vacancy = function() {
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

	window.radlibs.draw_new_lib_button = function ( click_handler ) {
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
		$button.click( click_handler );
		window.radlibs.row_with_vacancy().append( $button );
	};

	window.radlibs.collect_libs = function() {
				var libs = {};

		_.each( $( '.library' ), function( textarea ) {
			var $textarea,
				lib_name,
				lines;

			$textarea = $(textarea);
			lib_name = $textarea.attr( 'name' );
			lines = $textarea.val().split( "\n" );

			libs[window.radlibs.libcase(lib_name)] = lines;
		});

		return libs;
	};

	window.radlibs.libcase = function( title ) {
		return title[ 0 ].toUpperCase() + title.slice( 1 );
	};

	window.radlibs.add_new_lib = function() {
		var $new_lib_button,
			$textarea,
			$header,
			$div;

		$new_lib_button = $( '#new-lib-button' );
		$new_lib_button.detach();

		$div = $( '<div>' );
		$div.addClass( 'span4' );

		$textarea = $( '<textarea>' );
		$textarea.addClass( 'library' );
		$textarea.attr( 'rows', '10' );
		$textarea.attr( 'name', 'untitled' );
		$textarea.attr( 'id', 'untitled' );

		$header = $( '<h4>' );
		$header.text( radlibs.libcase( 'untitled' ) );

		$div.append( $header );
		$div.append( $textarea );

		radlibs.row_with_vacancy().append( $div );
		radlibs.row_with_vacancy().append( $new_lib_button );

		return $div;
	};

	show_signin_widget = function(event) {
		event.preventDefault();
		$( '#janrainEngageEmbed' ).toggle();
	};

	$(document).ready(function () {
		$( '#show-sign-in' ).click( show_signin_widget );
	});
})();