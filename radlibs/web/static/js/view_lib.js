(function () {
	'use strict';
	var new_rad;

	new_rad = function( event ) {
		event.preventDefault();
		var $done_button,
			$done_link,
			$form,
			$input,
			$parent,
			submit_rad,
			$this = $( this );

		$parent = $this.parent();
		$form = $( '<form>' );
		$input = $( '<input>' );
		$input.css( 'width', '80%' );
		$done_link = $( '<a>' );
		$done_link.attr( 'href', '#' );
		$done_button = $( '<img>' );
		$done_button.attr( 'src', '/static/img/accept-icon.png' );
		$done_button.attr( 'alt', 'done' );
		$done_button.css( 'margin-left', '10px' );
		$done_link.append( $done_button );

		$form.append( $input );
		$form.append( $done_link );

		$this.detach();
		$parent.append( $form );
		$input.focus();

		submit_rad = function ( event ) {
			event.preventDefault();
			var new_rad_url,
				rad;

			rad = $input.val().trim();
			new_rad_url = $( 'body' ).data( 'new_rad_url' );

			$.ajax( new_rad_url, {
				type: 'POST',
				data: {
					rad: rad
				},
				success: function( data, status, jqXHR ) {
					var $list,
						$li;

					$list = $( '.span8 ul' );
					$parent.text( rad );
					$li = $( '<li>' );
					$li.append( $this );
					$list.append( $li );
				},
				error: function(jqXHR, status, errorThrown) {
					alert( errorThrown );
				}
			});
		};
		$form.submit( submit_rad );
		$done_link.click( submit_rad );
	};

	$( document ).ready( function() {
		$( '#new-rad' ).click( new_rad );
	});
})();