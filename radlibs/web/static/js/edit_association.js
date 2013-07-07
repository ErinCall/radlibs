(function () {
	'use strict';
	var new_lib,
		test_radlib,
		draw_new_member_button,
		radlibs = window.radlibs;

	new_lib = function() {
		var $new_lib_button,
			$contents_div,
			$lib_div,
			$input,
			$form,
			submit_lib,
			$submit_link,
			$submit_button;

		$new_lib_button = $( '#new-lib-button' );
		$contents_div = $( '<div>' );
		$contents_div.addClass( 'span4' );
		$lib_div = $( '<div>' );
		$lib_div.addClass( 'lib-display' );
		$input = $( '<input>' );
		$input.css('width', '80%');
		$form = $( '<form>' );
		$submit_link = $( '<a>' );
		$submit_link.attr( 'href', '#' );
		$submit_button = $( '<img>' );
		$submit_button.attr( 'src', '/static/img/accept-icon.png' );
		$submit_button.css( 'margin-left', '10px');
		$submit_button.attr( 'alt', 'send' );

		submit_lib = function( event ) {
			event.preventDefault();
			var lib_name,
				new_lib_url;

			lib_name = $input.val().trim();
			new_lib_url = $( 'body' ).data( 'new_lib_url' );

			$.ajax( new_lib_url, {
				type: 'POST',
				data: { name: lib_name },
				success: function(data, status, jqXHR) {
					var lib_id,
						body = JSON.parse( data );
					if ( body[ 'status' ] == 'ok' ) {
						lib_id = body[ 'lib_id' ];
						document.location = '/lib/' + lib_id;
					} else {
						radlibs.display_error( body[ 'error' ]);
					}
				},
				error: function(jqXHR, status, errorThrown) {
					alert( errorThrown );
				}
			});
		};

		$form.submit( submit_lib );
		$submit_link.click( submit_lib );
		$submit_link.append( $submit_button );
		$form.append( $input );
		$form.append( $submit_link );
		$contents_div.append( $form );
		$contents_div.append( $lib_div );
		$new_lib_button.detach();
		radlibs.row_with_vacancy( 'lib-row' ).append( $contents_div );
		radlibs.row_with_vacancy( 'lib-row' ).append( $new_lib_button );
		$input.focus();
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

	draw_new_member_button = function() {
		var $row,
			invite_user,
			$new_member_div,
			$new_member_link;

		$row = radlibs.row_with_vacancy( 'member-row' );
		$new_member_div = $( '<div>' );
		$new_member_div.addClass( 'span4' );
		$new_member_link = $( '<a>' );
		$new_member_link.attr('href', '#');
		$new_member_link.text( 'Invite new member' );
		$new_member_div.append( $new_member_link );

		invite_user = function( event ) {
			event.preventDefault();
			var $form,
				$input,
				send_invite,
				$submit_link,
				$submit_button;

			$form = $( '<form>' );
			$input = $( '<input>' );
			$submit_link = $( '<a>' );
			$submit_link.attr( 'href', '#' );
			$submit_button = $( '<img>' );
			$submit_button.attr( 'src', '/static/img/accept-icon.png' );
			$submit_button.css( 'margin-left', '10px');
			$submit_button.attr( 'alt', 'send' );
			$submit_link.append( $submit_button );

			send_invite = function( event ) {
				event.preventDefault();
				var email;

				email = $input.val().trim();
				$form.remove();
				$.ajax( $( 'body' ).data( 'invite_user_url' ), {
					type: 'POST',
					data: {email: email},
					success: function(data, status, jqXHR) {
						var body = JSON.parse( data ),
							$row,
							$added_member_div;

						if ( body[ 'status' ] === 'ok' ) {
							if ( body[ 'action' ] === 'added' ) {
								$added_member_div = $( '<div>' );
								$added_member_div.addClass( 'span4' );
								$added_member_div.text( email );

								$row = radlibs.row_with_vacancy( 'member-row' );
								$row.append( $added_member_div );
							} else if ( body[ 'action' ] == 'invited' ) {
								radlibs.display_radlib( email + ' has been invited to join Radlibs!' );
							}
						} else {
							radlibs.display_error( body[ 'error' ]);
						}

						radlibs.row_with_vacancy( 'member-row' ).
							append( $new_member_div );
					},
					error: function(jqXHR, status, errorThrown) {
						alert( errorThrown );
					}
				});
			};

			$form.append( $input );
			$form.append( $submit_link );
			$form.submit( send_invite );
			$submit_link.click( send_invite );
			$new_member_div.detach();
			$row.append( $form );
			$input.focus();
		};

		$new_member_link.click( invite_user );
		$row.append( $new_member_div );
	};

	$(document).ready(function() {
		radlibs.draw_new_lib_button(new_lib);
		draw_new_member_button();
		$( '#fire' ).click( test_radlib );
		$( '#radlib-form' ).submit( test_radlib );
	});
})();
