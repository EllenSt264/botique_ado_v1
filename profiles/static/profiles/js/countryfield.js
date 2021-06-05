// To fix incorrect color for country select form on profile page
// as it is not required like it is on checkout

let countrySelected = $('#id_default_country').val();
if (!countrySelected) {
    $('#id_default_country').css('color', '#aab7c4');
}
$('#id_default_country').change(function() {
    countrySelected = $(this).val();
    if (!countrySelected) {
        $(this).css('color', '#aab7c4');
    } else {
        $(this).css('color', '#000');
    }
});