
function gnmplutoconverter_convert_master(itemid)
{
    /* the main function that kicks things off for the master. */

    /* first, show the dialog. */
    //$('#plutoconverter_item_id_label').html(itemid);
    $('#plutoconverter_item_id_input').attr('value',itemid);
    $('#plutoconverter_dlg').dialog("open");

    /* now, make sure it's populated */

}

function destroy_picker()
{
    $('#plutoconverter_parentpicker').remove();
}

function populate_project_dropdown()
{
    var comm = $('#id_picker_commission_dropdown').val();
    var mine = $('#id_picker_mine_only').val();
    //console.log("Current selected working group ID: " + wg);

    $.getJSON('/gnmplutoconverter/projects?comm=' + comm + '&mine=' + mine).success(function(data, jqXHR){
        $.each(data, function(idx,ptr){
            $('#id_picker_project_dropdown').append(
                $('<option>', {'value': ptr['vsid']}).html(ptr['title'])
            );
        });

    }).fail(function(jqXHR, errorThrown, status){
        $('#plutoconverter_parentpicker_error').html(errorThrown + '; ' + status);
        console.log("AJAX commission query failed");
    });
}

function populate_commission_dropdown()
{
    var wg = $('#id_picker_workinggroup_dropdown').val();
    var mine = $('#id_picker_mine_only').val();
    //console.log("Current selected working group ID: " + wg);

    $.getJSON('/gnmplutoconverter/commissions?wg=' + wg + '&mine=' + mine).success(function(data, jqXHR){
        $.each(data, function(idx,ptr){
            $('#id_picker_commission_dropdown').append(
                $('<option>', {'value': ptr['vsid']}).html(ptr['title'])
            );
        });

    }).fail(function(jqXHR, errorThrown, status){
        $('#plutoconverter_parentpicker_error').html(errorThrown + '; ' + status);
        console.log("AJAX commission query failed");
    });
}

function open_picker()
{
    var dlg=$('<div>', {'id': 'plutoconverter_parentpicker', 'style': 'display: none', 'title': 'Choose project'});
    $(document.body).append(dlg);

    dlg.dialog({
        autoOpen: true,
        width:600,
        close: destroy_picker,
    });

    var frm = $('<form>', {'id': 'plutoconverter_parentpicker_form'}).appendTo(dlg);
    var error_label = $('<p>', {'id': 'plutoconverter_parentpicker_error', 'class': 'error'}).appendTo(dlg);

    var lst = $('<ul>').appendTo(frm);

    var i = $('<li>').appendTo(lst);
    $('<input>', {'type': 'checkbox', 'checked': true, 'id': 'id_picker_mine_only'}).appendTo(i);
    $('<label>', {'for': 'id_picker_mine_only'}).html('Only show commissions belonging to me').appendTo(i);


    var i = $('<li>').appendTo(lst);
    var wd_drop = $('<select>', {'id': 'id_picker_workinggroup_dropdown'}).appendTo(i);
    $('<label>', {'for': 'id_picker_workinggroup_dropdown'}).html('Working group').appendTo(i);

    $.getJSON('/gnmplutoconverter/workinggroups?mine=' + $('#id_picker_mine_only').val()).success(function(data, jqXHR){
        console.log(data);
        $.each(data,function(idx,ptr){
            var attrs = {'value': ptr['uuid']};
            if('primary' in ptr){
                attrs['selected'] = true;
            }
            wd_drop.append($('<option>', attrs).html(ptr['name']));
        });
        populate_commission_dropdown();
    }).fail(function(jqXHR, errorThrown, status){
        error_label.html(errorThrown + '; ' + status);
        console.log("AJAX working group query failed");
    });

    var i = $('<li>').appendTo(lst);
    var commission_drop = $('<select>', {'id': 'id_picker_commission_dropdown'}).appendTo(i);
    $('<label>', {'for': 'id_picker_commission_dropdown'}).html('Commission').appendTo(i);

    var i = $('<li>').appendTo(lst);
    var project_drop = $('<select>', {'id': 'id_picker_project_dropdown'}).appendTo(i);
    $('<label>', {'for': 'id_picker_project_dropdown'}).html('Project').appendTo(i);
}

function build_dialog()
{
    var global_font_size = '1.6em'; //horrible i know but will work for time being
    var dlg=$('<div>', {'id': 'plutoconverter_dlg', 'style': 'display: none;', 'title': 'Convert to Pluto master'});
    var content_table = $('<table>').appendTo(dlg);

    var tr_item = $('<tr>').appendTo(content_table);
    $('<td>',{'style': 'text-align: right;'}).html('I would like to attach item: ').appendTo(tr_item);

    $('<input>', {'id': 'plutoconverter_item_id_input', 'type': 'textbox', 'disabled': true}).appendTo(
        $('<td>',{'id': 'plutoconverter_item_id_label','font-size': global_font_size})
    ).appendTo(tr_item);

    var tr_project = $('<tr>').appendTo(content_table);
    $('<td>',{'style': 'text-align: right;'}).html('To the project: ').appendTo(tr_project);

    var td_selector = $('<td>',{'id': 'plutoconverter_item_project_label','font-size': global_font_size}).appendTo(tr_project);
    $('<input>', {'id': 'plutoconverter_project_id_input', 'type': 'textbox', 'disabled': true}).appendTo(td_selector);
    $('<a>', {'href': '#', 'onclick': 'open_picker("project");'}).html("Choose...").appendTo(td_selector);

    var tr_commission = $('<tr>').appendTo(content_table);
    $('<td>',{'style': 'text-align: right;'}).html('within the commission: ').appendTo(tr_commission);

    var td_selector = $('<td>',{'id': 'plutoconverter_item_commission_label','font-size': global_font_size}).appendTo(tr_commission);
    $('<input>', {'id': 'plutoconverter_commission_id_input', 'type': 'textbox', 'disabled': true}).appendTo(td_selector);

    $(document.body).append(dlg);
}

$(document).ready(function(){
    build_dialog();
    $('#plutoconverter_dlg').dialog({
        autoOpen: false,
        width: 600,
    });
});