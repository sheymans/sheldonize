<!-- toggle script on selection of header column -->
function toggle(source) {
    checkboxes = document.getElementsByName('selection');
    for(var i in checkboxes)
      checkboxes[i].checked = source.checked;
  }

$( document ).ready(function() {
    // make sure bootstrap dropdowns work
    $('.dropdown-toggle').dropdown();
    // set the value for the signup button
    var timezone = jstz.determine();
    $('#signupbutton').val(timezone.name());
    
    // Counter on adding name:
    // using bootstrap-maxlength https://github.com/mimo84/bootstrap-maxlength/
    $('input#id_name').maxlength({
        threshold: 20,
        warningClass: "label label-info",
        limitReachedClass: "label label-warning",
        placement: 'bottom',
        message: '%charsTyped% / %charsTotal%'
    });


});


