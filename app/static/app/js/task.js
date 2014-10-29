function markdownlogic(id) {

    // The comment editing
$("#task-comment").markdown({autofocus:false,savable:true,
        onShow: function(e){

            // Transform the markdown content to HTML (in currentContent)
            var content = e.getContent(),
    currentContent = (typeof markdown == 'object') ? markdown.toHTML(content) : content

        var editable = e.$editable
        var oldElement = $('<'+editable.type+'/>')

        $(editable.attrKeys).each(function(k,v) {
            oldElement.attr(editable.attrKeys[k],editable.attrValues[k])
        })

    oldElement.html(currentContent)

    // Show the original div with the new HTML
    e.$editor.replaceWith(oldElement)

    $("#task-edit").click(function(){
        // At this point first remove the "Edit Note" button
        $('#task-edit').remove();
        $("#task-comment").markdown({autofocus:false,savable:true,height:"400",

            onSave: function(e) {
                // Send note to background
                $('#save-status').html('Saving...');
                $.ajax({
                    url:"/app/tasks/note/ajax/",
                    type:"POST",
                    data : { 'id': id, 'note': e.getContent() },
                    dataType:"json",
                })
                .done(function(data, textStatus, jqXHR) { $('#save-status').html('Note saved ' + (new Date()));
                })
                .fail(function(jqXHR, textStatus, errorThrown) { $('#save-status').html('Saving Failed! Try again.'); })
            .always(function(jqXHROrData, textStatus, jqXHROrErrorThrown)     { });
        //$('.md-editor > .md-footer > .btn[data-handler="cmdSave"]').html('Saved');
            },
        })
    }); 

        },
});
}





$( document ).ready(function() {

    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#tasks-nav').addClass('active');

    // This mess to detect when the input of a due date is null (previous versions always reset that to the old date.
    // TODO rather with a "clear" field on the time picker? Seems to be hard.
    //
    /*
       emptyval = false;
       $("#id_due").on("input", function (e) {
       if ($('#id_due').val() == '') {
       emptyval = true;
       }
       else {
       emptyval = false;
       }
       });

       $("#id_due").blur(function () {
       if (emptyval) {
       $('#id_due').val("");
       }
       });
       */

    // Put a datetimepicker on the due field:
    $('#id_due').datetimepicker({
        minuteStepping: 15,
    });

    // The comment editing logic
    // and the CSRF set up logic for the ajax posting of the note
    //
    //
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

    var id = $("#task-comment").attr( "task-id" )
        markdownlogic(id);


});
