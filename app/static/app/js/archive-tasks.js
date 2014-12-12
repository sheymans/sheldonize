$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#archive-nav').addClass('active');

    $('label[for="id_name"]').css('display', 'none');
    $('#id_name').focus();

    $('.table-hover tr > td').not('.selection').click(function() {
        var rowId = $(this).parent().data("rowKey");

        url_task = "/app/tasks/modal/update/" + rowId + "/";

        // we pick up a particular anchor a with that id that has been added in
        // sheldonize_table.html for calling the django-fm code
        $('#' + rowId).attr("href", url_task); 
        $('#'+rowId).trigger("click");

    });

    $( "body" ).on( "fm.ready", function() {
        // Set up javascript on modals (start date, end date dropdowns, as well
        // as markdown note taking.)
        //
        // Put a datetimepicker on the start and end field:
        $('#id_start').datetimepicker({
            minuteStepping: 15,
        });

        $('#id_end').datetimepicker({
            minuteStepping: 15,
        });

        // set up the markdown notes on the modal
        $.markdown_note("#task-comment", "task-id", "#task-edit", "/app/tasks/note/ajax/");

    });

});
