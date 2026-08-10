// Click tracking for outbound links.
//
// Vanilla rather than jQuery: this was the only thing several pages loaded an
// 86KB jQuery bundle from a third-party CDN to do.
document.addEventListener("DOMContentLoaded", function () {
    var links = document.querySelectorAll("a.outbound");
    Array.prototype.forEach.call(links, function (link) {
        link.addEventListener("click", function (event) {
            var href = link.getAttribute("href");
            var target = link.getAttribute("target");
            event.preventDefault(); // don't open the link yet
            // guarded: if analytics is blocked, gtag is undefined. The original
            // threw here, so the setTimeout never ran and the link never opened.
            if (typeof gtag === "function") {
                gtag("event", "click", {
                    event_label: href,
                    event_category: "link",
                });
            }
            setTimeout(function () {
                // now wait 300 milliseconds, then open the link as usual
                window.open(href, !target ? "_self" : target);
            }, 300);
        });
    });
});
