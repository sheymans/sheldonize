$( document ).ready(function() {

    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#preferences-nav').addClass('active');


   // $('label[for="id_day"]').css('display', 'none');
   // $('label[for="from_time"]').css('display', 'none');
   // $('label[for="to_time"]').css('display', 'none');

    // Put a datetimepicker on the from and to field:
     $('#id_from_time').datetimepicker({
         minuteStepping: 15,
         pickTime: true,
         pickDate: false,
         sideBySide: true
     });

     $('#id_to_time').datetimepicker({
         minuteStepping: 15,
         pickTime: true,
         pickDate: false,
         sideBySide: true
     });



});
