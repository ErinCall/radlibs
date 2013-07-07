(function () {
	'use strict';
	$( document ).ready( function() {
		var $jumbotron,
			$signin;

		$jumbotron = $( '.jumbotron' );
		$signin = $( '#janrainEngageEmbed' );

		$signin.detach();
		$signin.css('margin-left', '150px');
		$signin.css('margin-top', '0');
		$signin.css('position', 'relative');
		$jumbotron.append($signin);
		$signin.show();
	});

})();
