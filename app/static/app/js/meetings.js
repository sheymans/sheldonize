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


    function markdownlogic(id) {

        // The comment editing
        $("#meeting-comment").markdown({autofocus:false,savable:true, fullscreen: {enable: false},
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

            $("#meeting-edit").click(function(){
                // At this point first remove the "Edit Note" button
                $('#meeting-edit').remove();
                $("#meeting-comment").markdown({autofocus:false,savable:true, fullscreen: {enable: false}, height:"400",

                    onSave: function(e) {
                        // Send note to background
                        $('#save-status').html('Saving...');
                        $.ajax({
                            url:"/app/meetings/note/ajax/",
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





    $( "body" ).on( "fm.ready", function() {
        // Put a datetimepicker on the start and end field:
        $('#id_start').datetimepicker({
            minuteStepping: 15,
        });

        $('#id_end').datetimepicker({
            minuteStepping: 15,
        });

        // set up the markdown on the node
        var id = $("#meeting-comment").attr( "meeting-id" )
        markdownlogic(id);

    });


});
