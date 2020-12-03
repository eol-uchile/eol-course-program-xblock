/* Javascript for EolCourseProgramXBlock. */
function EolCourseProgramXBlock(runtime, element, settings) {

  var approved_icon    = `<span class="status"><i class="fa fa-check-circle" aria-hidden="true"></i></span>`;
  var reproved_icon    = `<span class="status"><i class="fa fa-times-circle" aria-hidden="true"></i></span>`;
  var loading_icon     = `<span class="status"><i class="fa fa-spinner fa-spin" aria-hidden="true"></i></span>`;
  var incomplete_icon  = `<span class="status"><i class="fa fa-chevron-circle-right" aria-hidden="true"></i></span>`;
  var not_allowed_icon = `<span class="status"><i class="fa fa-ban" aria-hidden="true"></i></span>`;

  $(function($) {

    var create_html_courses_list = ( courses_list ) => {
        var $list = $(element).find('#courses_list');
        courses_list.forEach( elem => {
          let $span = document.createElement('span');
          let $text = document.createTextNode(`${elem.display_name}`);
          $span.appendChild($text);
          let $div = document.createElement('div');
          $div.classList.add("items-body-content");
          $div.appendChild($span);
          $div.insertAdjacentHTML('beforeend', loading_icon );
          $list.append($div);
        });
    }

    var get_program_info = () => {
      $.get(settings.url_get_program_info, function(program, status){
        console.log(program);
        $(element).find(".program_name").text(program.program_name);
        create_html_courses_list(program.courses_list);
        var $ul = $(element).find('ul#courses_list');
        program.courses_list.forEach( elem => $ul.append($("<li>").text(`${elem.display_name} (${elem.course_id})`)) );
      });
    }
    if(settings.xblock_program_id) {
        get_program_info();
    }
    console.log(settings.url_get_program_info);
  
    });
}
