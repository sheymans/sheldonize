$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#meetings-nav').addClass('active');

    $('label[for="id_name"]').css('display', 'none');

    $('.table-hover tr > td').not('.selection').click(function() {
        var rowId = $(this).parent().data("rowKey");
        window.location = "/app/meetings/" + rowId + "/";
    });

});
