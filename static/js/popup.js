$(function() {
    
    if (Cookies.get('popup') === undefined && (/Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) == false) && $( window ).width() > 768) {
        Cookies.set('popup', 'true');
        $('#modalwelcome').modal('show'); 
    }
});
