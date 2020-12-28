/* https://www.tutorialrepublic.com/faq/how-to-keep-the-current-tab-active-on-page-reload-in-bootstrap.php  
* REQUIREMENTS: this code needs GLOBAL:
  var tablename
  var menu_type
*/

$(document).ready(function(){

    var this_menu_flag = 'activeTab_'+ tablename + '_' + menu_type;
    
    $('a[data-toggle="tab"]').on('show.bs.tab', function(e) {
        localStorage.setItem(this_menu_flag , $(e.target).attr('href'));
    });

    var activeTab_obj = localStorage.getItem(this_menu_flag);
    

    if(activeTab_obj){
        $('#myTab a[href="' + activeTab_obj + '"]').tab('show');
    }

});
