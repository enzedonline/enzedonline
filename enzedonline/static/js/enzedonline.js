// Usage: document.getElementById("id").innerHTML = convertUTCDateToLocalDate(new Date('02 Aug 2021 09:58:22'));
function convertUTCDateToLocalDate(date) {
    local_date = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    const date_options = { weekday: 'short', year: 'numeric', month: 'long', day: 'numeric' };
    const time_options = { hour: '2-digit', minute: '2-digit', hour12: false };
    return (local_date.toLocaleDateString(undefined, date_options) + ' ' + local_date.toLocaleTimeString(undefined, time_options));
}

$(document).ready(function(){
    $('a[href^="http://"]').attr('target', '_blank');
    $('a[href^="http://"]').attr('rel', 'nofollow noopener');
    $('a[href^="https://"]').attr('target', '_blank');
    $('a[href^="https://"]').attr('rel', 'nofollow noopener');
    });  