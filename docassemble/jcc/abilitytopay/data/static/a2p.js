/* DocAssemble page load event */
$(document).on('daPageLoad', function(){
  $('[data-toggle="tooltip"]').tooltip();
  $('a.help-widget').click(function(e) {
    e.preventDefault();
    $(this).addClass('opened');
    $(this).next().show();
  });
});

/* Manually redirect the user to clear cookies
 * after an idle timeout of 60 minutes. */

var idleTime = 0;

//Increment the idle time counter every minute.
var idleInterval = setInterval(timerIncrement, 60000); // 1 minute

//Zero the idle timer on mouse movement.
$(window).mousemove(function (e) {
    idleTime = 0;
});
$(window).keypress(function (e) {
    idleTime = 0;
});

function timerIncrement() {
    idleTime = idleTime + 1;
    if (idleTime > 60) { // 60 minutes
        window.location.href = "/user/sign-out?next=https://" + window.location.hostname;
    }
}
