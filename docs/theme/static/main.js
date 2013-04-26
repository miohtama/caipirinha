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

    /**
     * Move reST generated local navigation to a correct place.
     */
    function fixNavList() {
        $("#contents > ul").appendTo("#sidebar-inner").addClass("nav nav-list well");
    }

    /**
     * Easier to do in JS than hacking rst generator
     */
    function bootstrappifyRestructuredText() {
        // reST container CSS class conflicts with Bootstrap CSS class
        $("div.section").find(".container").removeClass("container");
    }

    function init() {
        setupGuidedArrival();
        setupMoreInfo();
        fixNavList();
        bootstrappifyRestructuredText();
    }

    $(init);

})(jQuery);