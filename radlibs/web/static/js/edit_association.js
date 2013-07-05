(function () {
	'use strict';
	var new_lib,
		save_all,
		radlibs = window.radlibs;

	new_lib = function() {
		var $header,
			$form,
			$input,
			$textarea,
			$done_link,
			$done_button,
			done_editing,
			$div;

		$div = radlibs.add_new_lib();
		$header = $div.find( 'h4' );
		$textarea = $div.find( 'textarea' );

		$form = $( '<form>' );
		$input = $( '<input>' );
		$input.val( $header.text().trim() );
		$input.css( 'width', '80%' );

		$done_link = $( '<a>' );
		$done_button = $( '<img>' );
		$done_button.attr( 'src', '/static/img/accept-icon.png' );
		$done_button.attr( 'alt', 'done' );
		$done_button.css( 'margin-left', '10px' );
		$done_link.append($done_button);

		$header.detach();
		$form.append( $input );
		$form.append($done_link);
		$div.prepend( $form );
		$input.focus().select();

		done_editing = function ( event ) {
			event.preventDefault();
			var new_title;

			new_title = $input.val();
			$header.text( radlibs.libcase( new_title ) );
			$div.prepend( $header );
			$form.remove();
			$textarea.attr( 'id', new_title );
			$textarea.attr( 'name', new_title );
		};

		$form.submit( done_editing );
		$done_button.click( done_editing );
	};

	save_all = function(event) {
		var $body,
			url,
			libs;
		event.preventDefault();

		$body = $( 'body' );
		url = '/association/' + $body.data( 'association_id' );

		libs = radlibs.collect_libs();
		$.ajax( url, {
			type: "POST",
			data: {
				libs: JSON.stringify(libs)
			},
			success: function( data, status, jqXHR ) {
			},
			error: function( jqXHR, status, errorThrown ) {
				alert( errorThrown );
			}
		});
	};

	$(document).ready(function() {
		radlibs.draw_new_lib_button(new_lib);
		$( '#save-all' ).click( save_all );
	});
})();