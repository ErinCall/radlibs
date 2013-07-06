(function() {
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
