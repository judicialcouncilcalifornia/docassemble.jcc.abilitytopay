/* DocAssemble page load event */
$(document).on('daPageLoad', function(){
  $('[data-toggle="tooltip"]').tooltip();
  $('a.help-widget').click(function(e) {
    e.preventDefault();
    $(this).addClass('opened');
    $(this).next().show();
  });
});
