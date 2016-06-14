$(document).ready(function(){

});

function load_storage_rule_info(itemid)
{
    $('#mvlibtool_sr_loading').show();

    $.getJSON('/gnmlibrarytool/storageruleinfo/' + itemid, function(data){
        console.log(data);
    }).fail(function(jqXHR, textStatus, errorThrown){
        $('#mvlibtool_error').html(errorThrown);
    }).finally(function(contentOrxhr, textStatus, xhrOrError){
        $('#mvlibtool_sr_loading').hide();
    });

}