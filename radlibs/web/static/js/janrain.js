(function() {
	'use strict';
	window.janrainWidgetOnload = function() {
		var $bypass_div,
			$bypass_link,
			$janrain_div;

		if ( $( 'body' ).data( 'bypass_login' ) === true ) {
			$janrain_div = $( '#janrainEngageEmbed' );
			$bypass_link = $( '<a>' );
			$bypass_link.attr( 'href', '/login_bypass' );
			$bypass_link.text( 'Use dev-only login bypass' );
			$bypass_div = $( '<div>' );
			$bypass_div.css( 'background', '#ffff00' );
			$bypass_div.append( $bypass_link );

			$janrain_div.append( $bypass_div );
		}
	};

	var $engage,
		$some_script;
	if (typeof window.janrain !== 'object') {
		window.janrain = {};
	}
	if (typeof window.janrain.settings !== 'object') {
		window.janrain.settings = {};
	}

	janrain.settings.tokenUrl = window.token_url;

	$( document ).ready( function() {
		janrain.ready = true;
	});

	$engage = $('<script>');
	$engage.attr( 'type', 'text/javascript' );
	$engage.attr( 'id', 'janrainAuthWidget' );

	if (document.location.protocol === 'https:') {
		$engage.attr( 'src', 'https://rpxnow.com/js/lib/radlibs/engage.js' );
	} else {
		$engage.attr( 'src', 'http://widget-cdn.rpxnow.com/js/lib/radlibs/engage.js' );
	}

	$some_script = $( 'script' ).first();
	$some_script.parent().prepend( $engage );

})();
