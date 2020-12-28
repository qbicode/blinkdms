/**
 * modal page calls other page ... 
 * @author  Steffen Kube (steffen@blink-dx.com)
 */

/** 
  @params need following GLOBAL variables ...
  tablename  ( of SOURCE window)
  x_dest_id  ( destination ID of element in TARGET window)
*/
function x_openwin(desttable, element_id, condition, prefix) {
  url_name = "?mod="+prefix+"obj_list&t="+ desttable +"&modal[id]="+ element_id;
  InfoWin  = window.open(url_name, desttable ,"scrollbars=yes,width=850,height=500,status=yes,resizable=yes");
  InfoWin.focus();
}


function x_input_remote(field_no, valuex, valtext) {
  valtexto = valuex +":"+ valtext
  id_attr_id='xfo'+field_no;
  if ((valuex == "") || (valtext == "")) valtexto = valuex + valtext;
  document.getElementById(id_attr_id).value = valuex;
  text_attr_id = id_attr_id+"shy";
  document.getElementById(text_attr_id).value = valtext;

}

function x_selback(pk_val, name, prefix) {
    if (window.opener != null)  {
        window.opener.x_input_remote( x_dest_id, pk_val, name );       
        location.href="?mod="+prefix+"winclose&t="+ tablename;
    } else alert("Warning: no parent window"); 
    
}
