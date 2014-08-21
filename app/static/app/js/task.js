$( document ).ready(function() {
 
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#tasks-nav').addClass('active');

    // This mess to detect when the input of a due date is null (previous versions always reset that to the old date.
    // TODO rather with a "clear" field on the time picker? Seems to be hard.
    //
    /*
    emptyval = false;
    $("#id_due").on("input", function (e) {
        if ($('#id_due').val() == '') {
            emptyval = true;
        }
        else {
            emptyval = false;
        }
    });

    $("#id_due").blur(function () {
        if (emptyval) {
            $('#id_due').val("");
        }
    });
    */

    // Put a datetimepicker on the due field:
     $('#id_due').datetimepicker({
         minuteStepping: 15,
     });
});

