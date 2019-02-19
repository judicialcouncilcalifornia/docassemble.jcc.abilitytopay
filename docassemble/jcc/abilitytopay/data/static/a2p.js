/* DocAssemble page load event */
$(document).on('daPageLoad', function(){
  $('[data-toggle="tooltip"]').tooltip();
});

/* Manually redirect the user to clear cookies
 * after an idle timeout of 60 minutes. */

var idleTime = 0;
$(document).on('daPageLoad', function () {
    //Increment the idle time counter every minute.
    var idleInterval = setInterval(timerIncrement, 60000); // 1 minute

    //Zero the idle timer on mouse movement.
    $(this).mousemove(function (e) {
        idleTime = 0;
    });
    $(this).keypress(function (e) {
        idleTime = 0;
    });
});

function timerIncrement() {
    idleTime = idleTime + 1;
    if (idleTime > 60) { // 60 minutes
        window.location.href = "/user/sign-out?next=https://" + window.location.hostname;
    }
}
