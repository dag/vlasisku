function search() {
    window.location = encodeURIComponent(document.getElementById('query').value);
    return false;
}

jQuery(document).ready(function ($) {
    $('a').tipTip({maxWidth: '600px'});
    $('#query').autocomplete('suggest/', {
        autoFill: true,
        matchCase: true,
        selectFirst: false
    });
    $(window).load(function () {
        $('#query').attr('autocomplete', 'off');
    });
});

