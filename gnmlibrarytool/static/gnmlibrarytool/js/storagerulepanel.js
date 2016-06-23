$(document).ready(function(){
    $('#mvlibtool_sr_loading').hide();
});

function load_storage_rule_info(itemid)
{
    itemPlayer.playerResize("small");
    $('#mvlibtool_sr_loading').show();
    $('#mvlibtool_sr_info').empty();
    $('#mvlibtool_error').empty();

    $.getJSON('/gnmlibrarytool/storageruleinfo/' + itemid, function(data){
        var table=$('#mvlibtool_sr_info');
        console.log(data);

        if(data.hasOwnProperty('status')){
            if(data['status']!="ok"){
                $('#mvlibtool_error').html("A server error occurred: " + data['error']);
                return;
            }
        }

        $.each(data, function(idx,ptr){
            var row=$('<tr>').appendTo(table);
            $('<td>').html(ptr['shapetag']).appendTo(row);
            var rules_cell=$('<td>').appendTo(row);
            if(ptr['rules']==null || ptr['rules'].length==0){
                $('<p>').html("No storage rule applied").appendTo(rules_cell);
                return;
            }
            $.each(ptr['rules'], function(idx,ptr){
                var rule_container=$('<p>').appendTo(rules_cell);
                var excludestr = ptr['not_storages'].join() + "," + ptr['not_groups'].join();
                var includestr = ptr['storages'].join() + "," + ptr['groups'].join();

                if(ptr['not_storages'].length==0 && ptr['not_groups'].length==0) excludestr = "(none)";
                if(ptr['storages'].length==0 && ptr['groups'].length==0) includestr = "(none)";

                rule_container.html("Minimum copies: " + ptr['storage_count'] +
                                    ".  Include: " +  includestr +
                                    "; Exclude: " + excludestr
                                    )
                $('<p>').append($('<a>',{'href': '/gnmlibrarytool/' + ptr['applies_to'][1]}).html('Applied from ' + ptr['applies_to'][0] + ' ' + ptr['applies_to'][1])).appendTo(rules_cell);
            });
        });
    }).fail(function(jqXHR, textStatus, errorThrown){
        $('#mvlibtool_error').html(errorThrown);
    }).always(function(contentOrXhr, textStatus, xhrOrError){
        $('#mvlibtool_sr_loading').hide();
    });

}