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
			$textarea,
			done_editing,
			$this = $(this);

		if (typeof event !== 'undefined' ) {
			event.preventDefault();
		}

		$anchor = $this.parents( 'a' );
		$container = $this.parents( '.span4' );
		$header = $container.find( 'h4' );
		$textarea = $container.find( 'textarea' );

		done_editing = function ( event ) {
			event.preventDefault();
			var new_title;

			new_title = $form.find( 'input' ).val();
			$header.text(radlibs.libcase(new_title));
			$container.prepend($header);
			$header.append($anchor);
			$anchor.append($this);
			$this.click(edit_lib_title);
			$form.remove();

			$textarea.attr('id', new_title);
			$textarea.attr('name', new_title);
		};

		$form = radlibs.form_input( $header.text().trim(), done_editing );
		$header.detach();
		$container.prepend( $form );

		$form.trigger( 'visible' );
	};


	$(document).ready(function() {
		if ( $( 'body' ).data( 'current_page' ) === 'live_demo' ) {
			$( '#radlib-form' ).submit( submit_radlib );
			$( '#fire' ).click(submit_radlib);
			$( '#radlib' ).focus().select();
			$( '.edit-button' ).click( edit_lib_title );
			radlibs.draw_new_lib_button( new_lib );
		}
	});
})();
