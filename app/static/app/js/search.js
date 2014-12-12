$( document ).ready(function() {

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

        // date time picker on end field
        $('#id_due').datetimepicker({
            minuteStepping: 15,
        });


        // set up the markdown notes on the modal
        $.markdown_note("#meeting-comment", "meeting-id", "#meeting-edit", "/app/meetings/note/ajax/");
        $.markdown_note("#task-comment", "task-id", "#task-edit", "/app/tasks/note/ajax/");

    });


});
