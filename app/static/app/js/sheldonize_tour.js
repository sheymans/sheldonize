$( document ).ready(function() {

       var hidden = "<div style=\"display: hidden\"></div>";
    // For the tour to work this has to be on each page that you tour to.
     tour = new Tour({
                    template: "<div class='popover tour'> <div class='arrow'></div> <h3 class='popover-title'></h3> <div class='popover-content'></div> <div class='popover-navigation'> <button class='btn btn-sheldonize btn-sheldonize-orange' data-role='prev'>prev</button> <button class='btn btn-sheldonize-orange' data-role='next'>next</button><button class='btn btn-sheldonize btn-sheldonize-primary' style='float: right;' data-role='end'>End Tour</button></div> </nav> </div>",
                 steps: [
                {
                     path: "/app/tasks/firsttime/",
                     orphan: true,
                     backdrop: true,
                     prev: -1,
                     next: 1,
                     content: "Welcome to Sheldonize!<br/><br/>We do things differently so let's do a 1-minute tour."
                 },
                 {
                     path: "/app/tasks/firsttime/",
                     element: "#preferences-nav",
                     content: "First things first. Let's check whether your work day preferences are OK."
                 },
                 {
                     element: ".table-container",
                     content: "We've added some working times that make sense (Mo-Fr, 8-5), but feel free to remove those and add new ones that fit your schedule. Sheldonize will always schedule work within these times.",
                     path: "/app/preferences/",
                 },
                 {
                     element: "#tasks-nav",
                     content: "Let's check out the tasks next.",
                     path: "/app/preferences/",
                 },

                 {
                     placement: 'left',
                     element: ".form-group",
                     content: "We can quickly add tasks here. Click <i>next</i> and we'll add that we need to walk the dog.",
                     prev: 0,
                     path: "/app/tasks/",
                     onNext: function(tour) { 
                         // add a test task
                         $('#id_name').val("Walk the dog");
                         $("button[name='new_task']").trigger("click");
                     },
                 },
                    // we add an artificial delay element
                {
                    title: "delay",
                    element: "#id_name",
                    template: hidden,
                    duration: 1000,
                    },
                 {
                     element: ".table > tbody > tr.new_thing",
                     prev: -1,
                     placement: 'left',
                     content: "You can add details to tasks by clicking on them. Click <i>next</i> to see that.",
                     path: "/app/tasks/",
                     onNext: function(tour) {
                         // click on the added test task
                        var rowId = $('table > tbody > tr').data("rowKey");
                        url_task = "/app/tasks/modal/update/" + rowId + "/";
                
                        // we pick up a particular anchor a with that id that has been added in
                        // sheldonize_table.html for calling the django-fm code
                        $('#' + rowId).attr("href", url_task); 
                        $('#'+rowId).trigger("click");
                                      },
                 },

                {
                    title: "delay",
                    element: ".table-container",
                    template: hidden,
                    duration: 1000,
                    },
 
                 {
                     placement: 'left',
                     element: "#div_id_when",
                     prev: -1,
                     content: "You can fill in useful details for your task here. We'll say that this task needs to be scheduled <i>This Week</i>.",
                     onNext: function(tour) {
                         // set the when to this week
                         $("#id_when").val('W');
                         // and submit
                         $('#submit-id-submit_save_task').trigger("click");
                     },
                     path: "/app/tasks/",
                 },

                {
                    title: "delay",
                    element: "#id_name",
                    template: hidden,
                    duration: 1000,
                    },
 
                 {
                     element: "#thisweek_tab",
                     placement: "bottom",
                     prev: -1,
                     content: "As we indicated that we want to do our task <i>This Week</i>, it is no longer in the Inbox, but can be found under the <i>This Week</i> tab.",
                     path: "/app/tasks/",
                 },
                 {
                     element: "#calculate-schedule",
                     content: "Sheldonize tries to schedule tasks that are marked as <i>Today</i> or <i>This Week</i>. Let's try to schedule our tasks.",
                     path: "/app/tasks/incomplete/thisweek/",
                     onNext: function(tour) {
                         // and submit
                         $('#calculate-schedule').trigger("click");
                     },
                 },
   {
                    title: "delay",
                    element: "#calculate-schedule",
                    template: hidden,
                    duration: 1000,
                    },

                 {
                     placement: 'left',
                     prev: -1,
                     element: "#schedule-nav",
                     content: "This is where you see your schedule. You can add meetings, import Google Calendar items, and recalculate a schedule with the push of a button.",
                     path: "/app/schedule/",
 
                 },
                 {
                     orphan: true,
                     content: "And that was a short introduction to Sheldonize. If you have more questions, do not hesitate and contact us at <a href='mailto:support@sheldonize.com'>support@sheldonize.com</a>.",
                     path: "/app/schedule/",
 
                 },









            ]
           });

     tour.init();
     tour.start();

});
