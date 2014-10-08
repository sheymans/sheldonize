function setup_schedule(eventfeed_url, viewtype) {

    $(document).ready(function() {

        // set the navigation right: (removed Oct 8 as we load this together
        // with task)
        //$(".navbar-sheldonize .nav li").removeClass("active");
        //$('#schedule-nav').addClass('active');

        // we want the token when we send pure ajax (this works because schedule.html has a form with the token):
        // See https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
        // BEGIN CSRF SETUP (move to sheldonize js?)
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        var csrftoken = getCookie('csrftoken'); 
        // More setup for those tokens following
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        // END CSRF SETUP

        $('#calendar').fullCalendar({
            header: {
                left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
            },
            // render title as HTML:
            eventRender: function(event, element, view) {                                          
                element.find('.fc-event-title').html(element.find('.fc-event-title').text());
            },
            defaultView: viewtype,
            // What day to show first (Monday=1)
            firstDay: 1,
            // do not display all day slot on top
            allDaySlot: false,
            // how long slots should take:
            slotDuration: '00:30:00',
            // from where show the calendar:
            minTime: "04:00:00",
            // view user starts on when opening schedule (from what time):
            scrollTime: "07:30:00",
            selectable: true,
            selectHelper: true,
            select: function(start, end) {
                var title = "";
                var eventData;
                // we want this event from an ajax call (django has to return this)
                eventData = {
                    title: "",
            start: start,
            end: end,
            color: "#ff6600",
                };
                // POST
                $.ajax({
                    url:"/app/meetings/ajax/",
                    type:"POST",
                    data : {'name': title, 'start' : String(start) , 'end': String(end) },
                    dataType:"json",
                    success: function(data) { $('#calendar').fullCalendar('renderEvent', data); }
                });
                // the below would throw the event immediately on the calendar, but ID is not set at that time, so we only add it upon success (see above).
                //          $('#calendar').fullCalendar('renderEvent', eventData); // stick? = true
                $('#calendar').fullCalendar('unselect');
            },
            editable: true,
            // When resizing, set existing meeting to new info::
            eventResize: function( event, jsEvent, ui, view ) {
                $.ajax({
                    url:"/app/meetings/ajax/",
                type:"POST",
                data : { 'id': event.id, 'name': event.title, 'start' : String(event.start) , 'end': String(event.end) },
                dataType:"json",
                success: function(data) {}
                });
            },
            eventDrop: function( event, jsEvent, ui, view ) {
                $.ajax({
                    url:"/app/meetings/ajax/",
                type:"POST",
                data : { 'id': event.id, 'name': event.title, 'start' : String(event.start) , 'end': String(event.end) },
                dataType:"json",
                success: function(data) {}
                });
            },
            events: {
                // this gets passed through via the function
                url: eventfeed_url,
            },
        });


        $('.dropdown-toggle').dropdown();

        // In mobile version of schedule, we have table of scheduleitems; we
        // need to be able to go to these tasks.
        //$('.table-hover tr > td').not('.selection').click(function() {
        //var rowId = $(this).parent().data("rowKey");
        //window.location = "/app/scheduleitems/" + rowId + "/";
        //});



    });
}
