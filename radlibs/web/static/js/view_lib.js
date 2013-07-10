(function () {
	'use strict';
	var new_rad;

	new_rad = function( event ) {
		event.preventDefault();
		var $done_link,
			$form,
			$input,
			$parent,
			submit_rad,
			$this = $( this );

		$parent = $this.parent();

		submit_rad = function ( event ) {
			event.preventDefault();
			var new_rad_url,
				rad;

			rad = $form.find( 'input' ).val().trim();
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
		$form = radlibs.form_input( '', submit_rad );

		$this.detach();
		$parent.append( $form );
		$form.trigger( 'visible' );
	};

	$( document ).ready( function() {
		$( '#new-rad' ).click( new_rad );
	});
})();
