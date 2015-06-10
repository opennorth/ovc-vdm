$(function() {
    $("a.home").attr('href', window.location.pathname.replace(/[^\/]*$/,''));
});