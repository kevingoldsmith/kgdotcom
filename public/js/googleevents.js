// add events for links
$(document).ready(function()
{
    $("a.outbound").each(function() {
        var href = $(this).attr("href");
        var target = $(this).attr("target");
        var text = $(this).text();
        $(this).click(function(event) { // when someone clicks these links
            event.preventDefault(); // don't open the link yet
            gtag('event', 'click', {'event_label': href, 'event_category': 'link'});
            setTimeout(function() { // now wait 300 milliseconds...
                window.open(href,(!target?"_self":target)); // ...and open the link as usual
            },300);
        });
    });
});
