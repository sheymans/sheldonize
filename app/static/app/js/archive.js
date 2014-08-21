$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#archive-nav').addClass('active');

    $('label[for="id_name"]').css('display', 'none');
    $('#id_name').focus();

    // Show recent rows in tasks with different background:
    $("tr td:contains('just now')").each(function(){
        // parent is the row as we go through tds
        $(this).addClass('just_added');
    }
    );
    $("tr td:contains('seconds ago')").each(function(){
        // parent is the row as we go through tds
        $(this).addClass('just_added');
    }
    );




});
