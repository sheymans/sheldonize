$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#projects-nav').addClass('active');

    $('label[for="id_name"]').css('display', 'none');


    $( "body" ).on( "fm.ready", function() {
        // Set up javascript on modals (start date, end date dropdowns, as well
        // as markdown note taking.)
        //
        // Put a datetimepicker on the start and end field:
        //$('#id_due').datetimepicker({
        //    minuteStepping: 15,
        //});

        // set up the markdown notes on the modal
        $.markdown_note("#task-comment", "task-id", "#task-edit", "/app/tasks/note/ajax/");

    });

    // Initialize the project tree:
    $('#projecttree').jstree({
        'core' : {
            'data' : {
                "url" : "/app/projects/ajax/",
            }
        }
    });

});
