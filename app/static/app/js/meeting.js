$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#meetings-nav').addClass('active');

    // Put a datetimepicker on the start and end field:
     $('#id_start').datetimepicker({
         minuteStepping: 15,
     });

     $('#id_end').datetimepicker({
         minuteStepping: 15,
     });
});

