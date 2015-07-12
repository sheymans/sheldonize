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
        $('#id_due').datetimepicker({
            minuteStepping: 15,
        });

        // set up the markdown notes on the modal
        $.markdown_note("#task-comment", "task-id", "#task-edit", "/app/tasks/note/ajax/");
        $.markdown_note("#project-comment", "project-id", "#project-edit", "/app/projects/note/ajax/");
        $.markdown_note("#habit-comment", "habit-id", "#habit-edit", "/app/habits/note/ajax/");

        // Add data attributes to labels:
        $(".sheldonize-form :checkbox").attr("data-labelauty","|");
        $(".sheldonize-form :checkbox").labelauty({same_width: true });
    });

    // Initialize the project tree:
    $('#projecttree').jstree({
        'core' : {
            'data' : {
                "url" : "/app/projects/ajax/",
            }
        },
        "state" : { "key" : "sheldonize_projects" },
        "plugins" : ["state"]
    });

});
