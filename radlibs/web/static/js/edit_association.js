(function () {
	'use strict';
	var new_lib,
		test_radlib,
		add_rad,
		draw_new_member_button,
		radlibs = window.radlibs;

	new_lib = function() {
		var $new_lib_button,
			$contents_div,
			$lib_div,
			$form,
			draw_lib_container,
			submit_lib;

		$new_lib_button = $( '#new-lib-button' );
		$contents_div = $( '<div>' );
		$contents_div.addClass( 'span4' );
		$lib_div = $( '<div>' );
		$lib_div.addClass( 'lib-display' );

		submit_lib = function( event ) {
			event.preventDefault();
			var lib_name,
				new_lib_url;

			lib_name = $form.find( 'input' ).val().trim();
			new_lib_url = $( 'body' ).data( 'new_lib_url' );

			$.ajax( new_lib_url, {
				type: 'POST',
				data: { name: lib_name },
				success: function(data, status, jqXHR) {
					var lib_id,
						body = JSON.parse( data );
					if ( body[ 'status' ] == 'ok' ) {
						lib_id = body[ 'lib_id' ];
						draw_lib_container( lib_id, lib_name );
					} else {
						if ( ! ~ body[ 'error' ].indexOf( 'not a valid lib name' )) {
							radlibs.display_error(
								body[ 'error' ] + "\nLib names must be a single capital letter followed by only lower case letters and underscores."
							);
						} else {
							radlibs.display_error( body[ 'error' ]);
						}
					}
				},
				error: function(jqXHR, status, errorThrown) {
					alert( errorThrown );
				}
			});
		};

		draw_lib_container = function( lib_id, lib_name ) {
			var $h4,
				$ul,
				$li,
				$new_rad_link;
			$form.remove();
			$h4 = $( '<h4>' );
			$h4.text( lib_name );
			$contents_div.prepend( $h4 );
			$lib_div.data( 'lib_id', lib_id );
			$new_rad_link = $( '<a>' );
			$new_rad_link.attr( 'href', '#' );
			$new_rad_link.text( 'Add new Rad' );
			$new_rad_link.click( add_rad );
			$ul = $( '<ul>' );
			$li = $( '<li>' );
			$ul.append( $li );
			$li.append( $new_rad_link );
			$lib_div.append( $ul );
		};

		$form = radlibs.form_input( '', submit_lib );
		$contents_div.append( $form );
		$contents_div.append( $lib_div );
		$new_lib_button.detach();
		radlibs.row_with_vacancy( 'lib-row' ).append( $contents_div );
		radlibs.row_with_vacancy( 'lib-row' ).append( $new_lib_button );
		$form.trigger( 'visible' );
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

	add_rad = function( event ) {
		var $form,
			$container,
			$li,
			submit_rad,
			lib_id,
			new_rad_url,
			$this = $( this );
		event.preventDefault();

		$container = $this.parents( 'div .lib-display' );
		$li = $this.parent( 'li' );
		new_rad_url = $( 'body' ).data( 'new_rad_url' );
		lib_id = $container.data( 'lib_id' );
		new_rad_url = new_rad_url.replace('%24lib_id', lib_id);

		submit_rad = function( event ) {
			var rad;
			event.preventDefault();

			rad = $form.find( 'input' ).val().trim();
			$.ajax( new_rad_url, {
				type: 'POST',
				data: { rad: rad },
				success: function( data, status, jqXHR ) {
					var $list,
						$new_li;
					console.log( data );
					$new_li = $( '<li>' );
					$li.text( rad );
					$new_li.append( $this );
					$list = $li.parent( 'ul' );
					$list.append( $new_li );
				},
				error: function( jqXHR, status, errorThrown ) {
					alert( errorThrown );
				}
			});
		};

		$form = radlibs.form_input( '', submit_rad );

		$this.detach();
		$li.append( $form );
		$form.trigger( 'visible' );
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
				send_invite;

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

			$form = radlibs.form_input( '', send_invite );

			$new_member_div.detach();
			$row.append( $form );
			$form.trigger( 'visible' );
		};

		$new_member_link.click( invite_user );
		$row.append( $new_member_div );
	};

	$(document).ready(function() {
		if ( $( 'body' ).data( 'current_page' ) === 'manage_associations' ) {
			radlibs.draw_new_lib_button(new_lib);
			draw_new_member_button();
			$( '#fire' ).click( test_radlib );
			$( '#radlib-form' ).submit( test_radlib );
			$( '.new-rad' ).click( add_rad );
		}
	});
})();
