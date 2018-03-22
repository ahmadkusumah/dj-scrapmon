django.jQuery(document).ready(function() {
    django.jQuery(".add-related").hide();
    django.jQuery(".change-related").hide();
});

function clicked(e)
{
    if(!confirm('Are you sure you want to run the scraper?'))e.preventDefault();
}