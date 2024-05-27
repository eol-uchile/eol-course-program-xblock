/* Javascript for EolCourseProgramStudioXBlock. */
function EolCourseProgramStudioXBlock(runtime, element, settings) {

  var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

  $(element).find('.save-button').bind('click', function(e) {
    var form_data = new FormData();
    var program_id = $(element).find('#course_programs_list').val();
    var next_course_enunciate = $(element).find('#next_course_enunciate').val();
    var program_courses_enrollment_modes = {};
    $("#courses_list select", $(element)).each(function(idx, el){
      program_courses_enrollment_modes[$(el).attr("name").replace(/^enrollmode_/, '')] = $("> option:selected", $(el)).val();
    });                                            
    if (program_id == null) {
      runtime.notify('cancel', {});
      e.preventDefault();
      return;
    }
    form_data.append('program_id', program_id);
    form_data.append('next_course_enunciate', next_course_enunciate);
    form_data.append('program_courses_enrollment_modes', JSON.stringify(program_courses_enrollment_modes));
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

  var course_programs = [];

  $(function($) {

    var create_html_courses_list = (program) => {
      var $ol = $(element).find('ol#courses_list');
      $ol.html('');
      program.courses_list.forEach(
        function(elem){
          var modes = program.courses_modes[elem.course_id];
          modes.unshift("Do not enroll")
          var selected_mode = settings.xblock_program_courses_enrollment_modes[elem.course_id];
          $ol.append(
            $("<li>")
            .text(`${elem.display_name} (${elem.course_id})`)
            .append(
              $("<div class='select-enrollment'>")
              .append($("<label>Enrollment Mode</label>"))
              .append(
                $("<select>")
                .attr("name", `enrollmode_${elem.course_id}`)
                .append(
                  modes.map(
                    mode => {
                      const option = $("<option>").val(mode).text(mode);
                      if (mode === selected_mode)
                        option.attr("selected", "selected");
                      return option;
                    }
                  )
                )
              )
            )
          );
        }
      );

      if(program.final_course) {
        $ol
        .append(
          $("<li>").text(`[FINAL] ${program.final_course.display_name} (${program.final_course.course_id})`)
        );
      }
    }

    var create_html_select = (course_programs) => {
      var $select = $(element).find('select#course_programs_list');
      course_programs.forEach( elem => $select.append($("<option>").attr('value', elem.program_id).text(elem.program_name)) );
      $select.change(() => {  
        var select_val = $select.val();
        var index = course_programs.findIndex(elem => elem.program_id == select_val);
        create_html_courses_list(course_programs[index])
      });
      if(settings.xblock_program_id) $select.val(settings.xblock_program_id).trigger('change');
    }

    var get_course_programs = () => {
      $.get(settings.url_get_course_programs, function(data, status){
        course_programs = data;
        $(element).find('#course_program_loading').hide();
        $(element).find('.course_program_studio').show();
        if(course_programs.length > 0) {
          create_html_select(course_programs);
        } else {
          $(element).find('.settings-list').text("Este curso no pertenece a ningún programa.");
          $(element).find('.save-button').hide();
        }
      });
    }

    $(element).find('.course_program_studio').hide();
    get_course_programs();

  });
}