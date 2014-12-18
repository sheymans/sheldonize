$( document ).ready(function() {
    // For the tour to work this has to be on each page that you tour to.
     tour = new Tour({
                    template: "<div class='popover tour'> <div class='arrow'></div> <h3 class='popover-title'></h3> <div class='popover-content'></div> <div class='popover-navigation'> <button class='btn btn-sheldonize btn-sheldonize-orange' data-role='prev'>prev</button> <button class='btn btn-sheldonize-orange' data-role='next'>next</button><button class='btn btn-sheldonize btn-sheldonize-primary' style='float: right;' data-role='end'>End Tour</button></div> </nav> </div>",
                 steps: [{
                     path: "/app/tasks/firsttime/",
                     element: "#preferences-nav",
                     content: "First thing you should do is check whether your work day preferences are OK for you."
                 },
                 {
                     element: ".table-container",
                     content: "We've added already some values that make sense (Mo-Fr, 8-5), but feel free to remove those and add new ones that fit your schedule. Sheldonize will always schedule work within these times.",
                     path: "/app/preferences/",
                 },
                 {
                     element: "#tasks-nav",
                     content: "Let's go check out the tasks next.",
                     path: "/app/preferences/",
                 },

            ]
           });

     tour.init();
     tour.start();

});
