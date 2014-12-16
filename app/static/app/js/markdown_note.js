;(function (jQuery) {
    jQuery.extend({
        markdown_note: function (comment_string, id_string, edit_string, ajax_save_url ) {
            // for example $.markdown_note("#meeting-comment', '#meeting-id", "#meeting-edit", "/app/meetings/note/ajax")

            function init() {

                // The id of the item (in the db)
                var id = $(comment_string).attr( id_string );

                // The comment editing
                $(comment_string).markdown({autofocus:false,savable:true, fullscreen: {enable: false}, resize: "vertical", 
                    onShow: function(e) {

                        // Transform the markdown content to HTML (in currentContent)
                        var content = e.getContent();
                        var currentContent = (typeof markdown == 'object') ? markdown.toHTML(content) : content;

                        var editable = e.$editable;
                        var oldElement = $('<'+editable.type+'/>');

                        $(editable.attrKeys).each(function(k,v) {
                            oldElement.attr(editable.attrKeys[k],editable.attrValues[k]);
                        });

                        oldElement.html(currentContent);

                        // Show the original div with the new HTML
                        e.$editor.replaceWith(oldElement);

                        $(edit_string).click( function() {
                            // At this point first remove the "Edit Note" button
                            $(edit_string).remove();
                            $(comment_string).markdown({autofocus:false,savable:true, fullscreen: {enable: false}, resize: "vertical",

                                onSave: function(e) {
                                    // Send note to background
                                    $('#save-status').html('Saving...');
                                    $.ajax({
                                        url: ajax_save_url,
                                        type:"POST",
                                        data : { 'id': id, 'note': e.getContent() },
                                        dataType:"json",
                                    })
                                    .done(function(data, textStatus, jqXHR) { $('#save-status').html('Note saved ' + (new Date()));
                                    })
                                    .fail(function(jqXHR, textStatus, errorThrown) { $('#save-status').html('Saving Failed! Try again.'); })
                                .always(function(jqXHROrData, textStatus, jqXHROrErrorThrown)     { });
                                },
                            })
                        }); 
                    },
                });
            }

            return init();
        }
    });
})(jQuery);


