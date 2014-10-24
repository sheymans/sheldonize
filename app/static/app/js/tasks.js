$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#tasks-nav').addClass('active');

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


    $('#id_name').focus();

    $('.table-hover tr > td').not('.selection').click(function() {
        var rowId = $(this).parent().data("rowKey");
        window.location = "/app/tasks/" + rowId + "/";
    });

});
