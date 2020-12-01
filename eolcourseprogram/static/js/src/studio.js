/* Javascript for EolCourseProgramStudioXBlock. */
function EolCourseProgramStudioXBlock(runtime, element) {

    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
  
    $(element).find('.save-button').bind('click', function(e) {
      var form_data = new FormData();
      var program_id = $(element).find('input[name=program_id]').val();
      form_data.append('program_id', program_id);
      if ($.isFunction(runtime.notify)) {
        runtime.notify('save', {state: 'start'});
      }
  
      $.ajax({
        url: handlerUrl,
        dataType: 'text',
        cache: false,
        contentType: false,
        processData: false,
        data: form_data,
        type: "POST",
        success: function(response){
          if ($.isFunction(runtime.notify)) {
            runtime.notify('save', {state: 'end'});
          }
        }
      });
      e.preventDefault();
  
    });
  
    $(element).find('.cancel-button').bind('click', function(e) {
      runtime.notify('cancel', {});
      e.preventDefault();
    });
}