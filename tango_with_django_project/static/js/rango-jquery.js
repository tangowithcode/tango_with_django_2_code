$(document).ready(function() {

    $('#about-btn').click(function() {
        alert("You clicked the button using JQuery!");
    });

    $('p').hover(
        function() {
            $(this).css('color', 'red');
        },
        function() {
            $(this).css('color', 'black');
        });

})