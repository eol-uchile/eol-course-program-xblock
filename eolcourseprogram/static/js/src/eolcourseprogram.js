/* Javascript for EolCourseProgramXBlock. */
function EolCourseProgramXBlock(runtime, element, settings) {

  var approved_icon    = `<span class="status"><i class="fa fa-check-circle" aria-hidden="true"></i></span>`;
  var reproved_icon    = `<span class="status"><i class="fa fa-times-circle" aria-hidden="true"></i></span>`;
  var loading_icon     = `<span class="status"><i class="fa fa-spinner fa-spin" aria-hidden="true"></i></span>`;
  var incomplete_icon  = `<span class="status"><i class="fa fa-chevron-circle-right" aria-hidden="true"></i></span>`;
  var not_allowed_icon = `<span class="status"><i class="fa fa-ban" aria-hidden="true"></i></span>`;

  $(function($) {

    var fill_counters_and_percentage = (approved_count, courses_total_count) => {
      /*
        Fill approved/total count
        Fill progress bar percentage
      */
      let percentage = (approved_count/courses_total_count) * 100;
      $(element).find('.approved_count').text(approved_count);
      $(element).find('.courses_count').text(courses_total_count);
      $(element).find('.progress-bar').text(`${Math.round(percentage)}%`);
      $(element).find('.progress-bar').css("width", `${percentage}%`);
    }

    var create_html_course_element = ( elem ) => {
      // span text
      let $span = document.createElement('span');
      let $text = document.createTextNode(`${elem.display_name}`);
      $span.appendChild($text);
      // element container
      let $div = document.createElement('div');
      $div.classList.add("items-body-content");
      // insert span text into element container
      $div.appendChild($span);
      return $div;
    }
    
    var create_html_courses_list = ( courses_list ) => {
      /*
        Create a list with all the course in the program
      */
      var $list = $(element).find('#courses_list');
      courses_list.forEach( elem => {
        /*
          Create each course element
        */
        let $div = create_html_course_element(elem);
        // insert status icon
        $div.insertAdjacentHTML('beforeend', elem.passed ? approved_icon : incomplete_icon );
        // create 'a' element with the course home page url
        let $a = document.createElement('a');
        $a.href = elem.course_url;
        $a.target = '_blank';
        // append div into 'a' element
        $a.append($div);
        // insert the new course element into the list
        $list.append($a);
      });
    }

    var create_html_final_course = (course, is_allowed) => {
      /*
        Create final course section
        is_allowed: True if course.is_passed == course_list.length 
      */
      var $list = $(element).find('#final_course_list');
      let $div = create_html_course_element(course);
      if(is_allowed) {
        // insert status icon
        $div.insertAdjacentHTML('beforeend', course.passed ? approved_icon : incomplete_icon );
        // create 'a' element with the course home page url
        let $a = document.createElement('a');
        $a.href = settings.url_enroll_and_redirect;
        $a.target = '_blank';
        // append div into 'a' element
        $a.append($div);
        // insert the new course element into the list
        $list.append($a);
      } else {
        // insert status icon (not allowed)
        $div.insertAdjacentHTML('beforeend', not_allowed_icon );
        $div.classList.add("course-disabled");
        $list.append($div);
      }
    }

    var get_program_info = () => {
      /*
        Get program info from API
      */
      $.get(settings.url_get_program_info, function(program, status){
        console.log(program);
        $(element).find(".program_name").text(program.program_name);
        create_html_courses_list(program.courses_list);
        fill_counters_and_percentage(program.approved_count, program.courses_list.length);
        // show final course if exists
        if (program.final_course) {
          create_html_final_course(program.final_course, program.final_course_allowed);
        } else {
          $(element).find(".final_course_instruction").text('');  // Remove final course instruction
          $(element).find(".final_course_section").hide();
        }
      });
    }

    // Check if the component is correctly configured
    if(settings.xblock_program_id) {
        get_program_info();
    }
  
    });
}
