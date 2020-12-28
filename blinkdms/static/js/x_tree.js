/* tree view, need x_tree.js */

var plus_element_id = 0;
var span_obj   = null; // SPAN object of parent, not available, if it is the root
var x_tree_isroot = 0; // the plus element is in the ROOT UL ?
x_init_tree();

function x_init_tree() {
  var toggler = document.getElementsByClassName("x_tree_caret");
  var i;
  for (i = 0; i < toggler.length; i++) {
    toggler[i].addEventListener("click", function() {
      this.parentElement.querySelector(".x_tree_nested").classList.toggle("x_tree_active");
      this.classList.toggle("x_tree_caret-down");
    });
  }
}

/* modify a FORM variable */
function x_form_modi( mo_id, objid, isroot=0 ) {
    plus_element_id = objid
    x_tree_isroot   = isroot
    document.editform2.elements['argu[x.CON_CONTACT_ID]'].value = mo_id;
}

function x_do_out(data) {

  if (data['error']) {
     alert("ERROR: "+ data['error']['text'] )
     return;
  }
  
  if ( !data['data'] ) {
    alert("ERROR: Did not get an object-ID." )
    return;
  }
  
  new_obj_id = data['data']['id']
  new_name   = document.editform2.elements['argu[x.NAME]'].value

  // create new HTML elements
  var node = document.createElement("LI");  
  var node_SPAN = document.createElement("SPAN"); 
  node_SPAN.setAttribute("class", "x_tree_caret-down"); 
  
  // add event to new element
  node_SPAN.addEventListener("click", function() {
      this.parentElement.querySelector(".x_tree_nested").classList.toggle("x_tree_active");
      this.classList.toggle("x_tree_caret-down");
    });
  
  
  var node_A = document.createElement("A"); 
  node_A.setAttribute("href"  , '?mod=oLOCATION/devs&id='+ new_obj_id );
  node_A.setAttribute("target", 'i_right' );
  var A_textnode = document.createTextNode(new_name);
  node_A.appendChild(A_textnode);    
  
  button_HTML = '<button class="btn x_btn-transparent"  type="button" data-toggle="modal" data-target="#xLocAdd" onClick="x_form_modi( '+new_obj_id+', this )">' +
    '<img src="res/images/feather/plus.svg" border=0></button>';
  
  node.appendChild(node_SPAN);  
  node.appendChild(node_A);  
  node.insertAdjacentHTML("beforeend", button_HTML); 
  
  li_parent = plus_element_id.parentElement;
  
  if (x_tree_isroot) {
    // element added to ROOT
    ul_obj  = li_parent;
    ul_obj.appendChild(node); 
    return;
  }
  
  ul_obj  = li_parent.querySelector("ul");
  ul_obj.appendChild(node); 
  
  // x_init_tree(); // RE-INIT javascript onclink funcion
  ul_obj.classList.add("x_tree_active");
  
  if (span_obj) {
    span_class = span_obj.getAttribute("class");
    span_obj.classList.add("x_tree_caret-down");
  }
  
}

function x_add_child() {

  if (!x_tree_isroot) {
    // normal sub leaf
    li_parent = plus_element_id.parentElement;
    span_obj  = li_parent.querySelector("span")
    ul_obj    = li_parent.querySelector("ul")
    if (!ul_obj) {
       var ul_obj = document.createElement("UL");
       ul_obj.setAttribute("class", "x_tree_nested"); 
       li_parent.appendChild(ul_obj);
       span_class = 'x_tree_caret';
       if (span_obj) { // {# otherwise root #}
          span_obj.classList.toggle("x_tree_caret");
       }
      
    }
  }
  
  var new_name   = document.editform2.elements['argu[x.NAME]'].value
  var mo_cont_id = document.editform2.elements['argu[x.CON_CONTACT_ID]'].value
  
  $.ajax({
        url : '/api/rest?mod=obj_new&t=LOCATION&argu[x.NAME]='+new_name+'&argu[x.CON_CONTACT_ID]='+mo_cont_id+'&go=1',
        success: function(data) {
            x_do_out(data);
        }
  });

  
}