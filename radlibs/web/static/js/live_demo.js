(function() {
	'use strict';

	var submit_radlib,
		new_lib,
		display_radlib,
		edit_lib_title,
		display_error,
		radlibs = window.radlibs;

	submit_radlib = function( event ) {
		event.preventDefault();
		var rad,
			libs = radlibs.collect_libs();

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

	new_lib = function () {
		var $div,
			$edit_link,
			$edit_button,
			$header;

		$div = radlibs.add_new_lib();
		$header = $div.find( 'h4' );

		$edit_link = $( '<a>' );
		$edit_button = $( '<img>' );
		$edit_button.attr( 'src', '/static/img/edit-icon.png' );
		$edit_button.attr( 'alt', 'edit' );
		$edit_link.append( $edit_button );
		$header.append( $edit_link );

		_.bind( edit_lib_title, $edit_button )();
	};

	edit_lib_title = function( event ) {
		var $container,
			$header,
			$form,
			$anchor,
			$input,
			$textarea,
			$done_link,
			$done_button,
			done_editing,
			$this = $(this);

		if (typeof event !== 'undefined' ) {
			event.preventDefault();
		}

		$anchor = $this.parents( 'a' );
		$container = $this.parents( '.span4' );
		$header = $container.find( 'h4' );
		$textarea = $container.find( 'textarea' );

		$input = $( '<input>' );
		$input.val( $header.text().trim() );
		$input.css( 'width', '80%' );

		$done_link = $( '<a>' );
		$done_button = $( '<img>' );
		$done_button.attr( 'src', '/static/img/accept-icon.png' );
		$done_button.attr( 'alt', 'done' );
		$done_button.css( 'margin-left', '10px' );
		$done_link.append($done_button);

		$form = $( '<form>' );
		$form.append( $input );
		$form.append( $done_link );
		$header.detach();
		$container.prepend( $form );

		$input.focus().select();

		done_editing = function ( event ) {
			event.preventDefault();
			var new_title;

			new_title = $input.val();
			$header.text(radlibs.libcase(new_title));
			$container.prepend($header);
			$header.append($anchor);
			$anchor.append($this);
			$this.click(edit_lib_title);
			$form.remove();

			$textarea.attr('id', new_title);
			$textarea.attr('name', new_title);
		};

		$form.submit(done_editing);
		$done_button.click(done_editing);
	};


	$(document).ready(function() {
		$( '#radlib-form' ).submit( submit_radlib );
		$( '#fire' ).click(submit_radlib);
		$( '#radlib' ).focus().select();
		$( '.edit-button' ).click( edit_lib_title );
		radlibs.draw_new_lib_button( new_lib );
	});
})();