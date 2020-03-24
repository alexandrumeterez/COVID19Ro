(function($) {
	"use strict";

	var fullHeight = function() {

		$('.js-fullheight').css('height', $(window).height());
		$(window).resize(function(){
			$('.js-fullheight').css('height', $(window).height());
		});

	};

	fullHeight();
    console.log("TEST");

	$('#sidebarCollapse').on('click', function () {
	    console.log("TESTevent");

      $('#sidebar').toggleClass('active');
      	    console.log("TESTeventafter");

  });
      console.log("TESTafteronclick");


})(jQuery);
