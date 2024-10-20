$(window).on('load', function () {
    console.log("Page loaded, script started");
    function animateOnScroll() {
        console.log("Scroll detected");
        $('.product_item').each(function () {
            let elementPosition = $(this).offset().top;
            let scrollPosition = $(window).scrollTop();
            let windowHeight = $(window).height();

            console.log("Element position:", elementPosition, "Scroll position:", scrollPosition);

            if (elementPosition < scrollPosition + windowHeight - 100) {
                $(this).addClass('animate__fadeInUp');
                console.log("Animation added to element:", $(this));
            }
        });
    }

    // Initial check on page load
    animateOnScroll();

    // Check again on scroll
    $(window).scroll(animateOnScroll);
});
