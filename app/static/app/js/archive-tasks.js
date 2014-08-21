$( document ).ready(function() {
    // set the navigation right:
    $(".navbar-sheldonize .nav li").removeClass("active");
    $('#archive-nav').addClass('active');

    $('label[for="id_name"]').css('display', 'none');
    $('#id_name').focus();

    $('.table-hover tr > td').not('.selection').click(function() {
        var rowId = $(this).parent().data("rowKey");
        window.location = "/app/tasks/" + rowId + "/";
    });




});
