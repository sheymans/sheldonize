$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#meetings-nav').addClass('active');

    $('label[for="id_name"]').css('display', 'none');

    $('.table-hover tr > td').not('.selection').click(function() {
        var rowId = $(this).parent().data("rowKey");
         
        url_meeting = "/app/meetings/modal/update/" + rowId + "/";

        // we pick up a particular anchor a with that id that has been added in
        // sheldonize_table.html for calling the django-fm code
        $('#' + rowId).attr("href", url_meeting); 
        $('#'+rowId).trigger("click");
         
                
        });
    
    $( "body" ).on( "fm.ready", function() {
            // Put a datetimepicker on the start and end field:
        $('#id_start').datetimepicker({
            minuteStepping: 15,
        });

        $('#id_end').datetimepicker({
            minuteStepping: 15,
        });


    });


});
