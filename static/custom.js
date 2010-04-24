function search() {
    window.location = encodeURIComponent(document.getElementById('query').value);
    return false;
}

jQuery(document).ready(function ($) {
    $('a').tipTip({maxWidth: '600px'});
    $('#query').autocomplete('suggest/');
});

