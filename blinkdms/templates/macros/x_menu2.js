/* https://www.tutorialrepublic.com/faq/how-to-keep-the-current-tab-active-on-page-reload-in-bootstrap.php  
* REQUIREMENTS: this code needs GLOBAL:
  var tablename
  var menu_type
*/

$(document).ready(function(){

    /* remember, if the TAB was shown/collapsed last time during this session; store this status in sessionStorage */
    var this_menu_flag = 'activeTab_'+ tablename + '_' + menu_type;
    
    $('a[data-toggle="tab"]').on('show.bs.tab', function(e) {
        localStorage.setItem(this_menu_flag , $(e.target).attr('href'));
    });

    var activeTab_obj = localStorage.getItem(this_menu_flag);
    if(activeTab_obj){
        $('#myTab a[href="' + activeTab_obj + '"]').tab('show');
    }
    
    /* remember, if the MENU was shown/collapsed last time during this session; store this status in sessionStorage */
    var menu_obj = document.getElementById("q_main_menu_button");
    menu_obj.addEventListener("click", function() {
        var menu_obj = document.getElementById("q_main_menu");
        temp_lst = menu_obj.classList;
        if ( temp_lst.contains('show') ) {
           sessionStorage.setItem("obj.menu.show", 0);
        } else {
           sessionStorage.setItem("obj.menu.show", 1);
        }
    });
    
    var current_menu_show = sessionStorage.getItem("obj.menu.show");
    if (current_menu_show=='1') {
      $('#q_main_menu').collapse('show');
      a=1;
    }



});
