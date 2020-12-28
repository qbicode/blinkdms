// {# left right select box #}
// support two forms: f1 and f2

/* F1 */
$("#f1btnLeft").click(function () {
    var selectedItem = $("#f1rightValues option:selected");
    $("#f1leftValues").append(selectedItem);
});

$("#f1btnRight").click(function () {
    var selectedItem = $("#f1leftValues option:selected");
    $("#f1rightValues").append(selectedItem);
});

$("#f1rightValues").change(function () {
    var selectedItem = $("#f1rightValues option:selected");
    // $("#f1txtRight").val(selectedItem.text());
});

/* F2 */
$("#f2btnLeft").click(function () {
    var selectedItem = $("#f2rightValues option:selected");
    $("#f2leftValues").append(selectedItem);
});

$("#f2btnRight").click(function () {
    var selectedItem = $("#f2leftValues option:selected");
    $("#f2rightValues").append(selectedItem);
});

$("#f2rightValues").change(function () {
    var selectedItem = $("#f2rightValues option:selected");
    // $("#f1txtRight").val(selectedItem.text());
});

function x_on_submit() {

    if ( $('#f1rightValues').length ) {
        values_old = $('#f1rightValues').val();
        var selectedArray = new Array();
        var selObj = document.getElementById('f1rightValues'); 
        var i;
        var count = 0;
        for (i=0; i<selObj.options.length; i++) { 
            selectedArray[count] = selObj.options[i].value;
            count++; 
        } 
        document.editform.reviewers.value = selectedArray;
    }
    
    if ( $('#f2rightValues').length ) {
        values_old = $('#f2rightValues').val();
        var selectedArray = new Array();
        var selObj = document.getElementById('f2rightValues'); 
        var i;
        var count = 0;
        for (i=0; i<selObj.options.length; i++) { 
            selectedArray[count] = selObj.options[i].value;
            count++; 
        } 
        document.editform.releasers.value = selectedArray;
    }
    
    document.editform.submit();
}

