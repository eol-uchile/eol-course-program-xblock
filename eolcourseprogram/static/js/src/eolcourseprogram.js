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
      let $span_parent = document.createElement('span');
      $span_parent.classList.add("items-body-content");
      // insert span text into element container
      $span_parent.appendChild($span);
      return $span_parent;
    }
    
    var create_html_courses_list = ( courses_list ) => {
      /*
        Create a list with all the course in the program
      */
      var $list = $(element).find('#courses_list');
      let modes = settings.xblock_program_courses_enrollment_modes;
      courses_list.forEach( elem => {
        /*
          Create each course element
        */
        let $span = create_html_course_element(elem);
        // insert status icon
        $span.insertAdjacentHTML('beforeend', elem.passed ? approved_icon : incomplete_icon );
        // create 'a' element with the course home page url
        let $a = document.createElement('a');
        
        $a.href = elem.course_url;
        $a.target = '_blank';
        $a.setAttribute('data-course-id', elem.course_id);
        // append span into 'a' element
        $a.append($span);
        // insert the new course element into the list
        $list.append($a);

        $a.addEventListener('click', function(event) {
          // Prevent the default behavior of the anchor element (i.e., navigating to a new page)
          event.preventDefault();        
          fetch(`/eol_course_programs/enroll_student/${elem.course_id}` , {
            method: 'POST',
            // Include any data you need to send to the backend
            body: JSON.stringify({mode:modes[elem.course_id]}),
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken(), // Include the CSRF token in the headers (https://docs.djangoproject.com/en/5.0/howto/csrf/)
            },
            mode: 'same-origin'            
          }).then(function(response) {
              // Handle the response from the backend if needed
              window.location.assign($a.href);              
              
          }).catch(function(error) {
              // Handle errors if the request fails
              $(document).find('.eolcourseprogram_block').append($('<div>').addClass('error-message').text(`Ha ocurrido un error: ${error}`));
              console.error('Error:', error);
          });
            
          // If needed, you can also navigate to the href URL after executing the backend code
          // window.location.href = href;
        });

      });
    }

    var create_html_final_course = (course, is_allowed) => {
      /*
        Create final course section
        is_allowed: True if course.is_passed == course_list.length 
      */
      var $list = $(element).find('#final_course_list');
      let $span = create_html_course_element(course);
      if(is_allowed) {
        // insert status icon
        $span.insertAdjacentHTML('beforeend', course.passed ? approved_icon : incomplete_icon );
        // create 'a' element with the course home page url
        let $a = document.createElement('a');
        $a.href = settings.url_enroll_and_redirect;
        $a.target = '_blank';
        // append span into 'a' element
        $a.append($span);
        // insert the new course element into the list
        $list.append($a);
      } else {
        // insert status icon (not allowed)
        $span.insertAdjacentHTML('beforeend', not_allowed_icon );
        $span.classList.add("course-disabled");
        $list.append($span);
      }
    }

    var get_program_info = () => {
      /*
        Get program info from API
      */
      $.get(settings.url_get_program_info, function(program, status){
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
    
    const getCSRFToken = () => {
      let cookieValue = null;
      if (document.cookie) {cookieValue = document.cookie.split('; ').find((row) => row.startsWith("csrftoken="))?.split("=")[1];}
      return decodeURIComponent(cookieValue);
    }
    // Check if the component is correctly configured
    if(settings.xblock_program_id) {
        get_program_info();
    }
  
    });
}
