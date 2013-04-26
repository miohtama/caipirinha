(function($) {

    "use strict";

    function init() {
        if(window.location.hash == "#help") {
            $("#guided-arrival").show();
        }
    }

    $(init);

})(jQuery);