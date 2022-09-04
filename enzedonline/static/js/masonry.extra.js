let timeout = false;
const masonry_layout = () => {
    $('.grid').masonry('layout');
}
window.onload = function() {
    masonry_layout;
}
window.onresize = function() {
    clearTimeout(timeout);
    timeout = setTimeout(masonry_layout, 500);
}