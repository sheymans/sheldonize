$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#habits-nav').addClass('active');

    $('label[for="id_name"]').css('display', 'none');

    // Show recent rows in tasks with different background:
    $("tr td:contains('just now')").each(function(){
        // parent is the row as we go through tds
        $(this).parent().addClass('success');
    }
    );
    $("tr td:contains('seconds ago')").each(function(){
        // parent is the row as we go through tds
        $(this).parent().addClass('success');
    }
    );


    // Replace the li.next and li.previous
    $('li.next a').html("&rarr;");
    $('li.previous a').html("&larr;");

    $('.table-hover tr > td').not('.selection').click(function() {
        var rowId = $(this).parent().data("rowKey");

        url_habit = "/app/habits/modal/update/" + rowId + "/";

        // we pick up a particular anchor a with that id that has been added in
        // sheldonize_table.html for calling the django-fm code
        $('#' + rowId).attr("href", url_habit); 
        $('#'+rowId).trigger("click");

    });

    $( "body" ).on( "fm.ready", function() {
        // Set up javascript on modals (start date, end date dropdowns, as well
        // as markdown note taking.)
        //
        // Put a datetimepicker on the start and end field:
        $('#id_due').datetimepicker({
            minuteStepping: 15,
        });

        // set up the markdown notes on the modal
        $.markdown_note("#habit-comment", "habit-id", "#habit-edit", "/app/habits/note/ajax/");

    });

});
