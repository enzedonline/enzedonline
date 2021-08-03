//  Dropdown menu aligns with right of button, lose focus after click
$(document).ready(function() {
    $('.dropright button').on("click", function(e) {
        e.stopPropagation();
        e.preventDefault();

        if (!$(this).next('div').hasClass('show')) {
        $(this).next('div').addClass('show');
        } else {
        $(this).next('div').removeClass('show');
        }
    });
});
$('.navbar-toggler').mouseup(function(){
    $(this).blur();
})
 