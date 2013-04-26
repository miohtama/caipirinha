(function($) {

    "use strict";

    function setupGuidedArrival() {
        if(window.location.hash == "#help") {
            $("#guided-arrival").show();
        }
    }

    function setupMoreInfo() {
        $(".advice").on("click", ".more-info-toggle", function(e) {
            e.preventDefault();
            var moreInfo = $(e.delegateTarget).find(".more-info");
            moreInfo.slideToggle();
            return false;
        });
    }

    function init() {
        setupGuidedArrival();
        setupMoreInfo();
    }

    $(init);

})(jQuery);