$(document).ready(function() {
    // Adds hover popup image for references.
$('.hover-trigger').hover(function() {
// Get the image URL from data attribute
var imgSrc = $(this).data('img');
var imgHtml = '<img src="' + imgSrc + '" style="width: 200px;" alt="Popup Image">';
$('.hover-image').html(imgHtml).css({
  'top': $(this).offset().top - 100, // Adjust this value to position the popup
  'left': $(this).offset().left + 600 ,
  'display': 'block',
 
});
}, function() {
// Hide the image popup when not hovering
$('.hover-image').hide();
});
});