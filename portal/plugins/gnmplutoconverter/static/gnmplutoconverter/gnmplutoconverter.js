
function gnmplutoconverter_convert_master(itemid)
{
    /* the main function that kicks things off for the master. */

    /* first, show the dialog. */
    $('#plutoconverter_item_id_input').attr('value',itemid);
    $('#plutoconverter_dlg').dialog("open");
    $('#plutoconverter_project_id_input').empty();
    $('#plutoconverter_commission_id_input').empty();
    /* now, make sure it's populated */

}

function destroy_picker()
{
    $('#plutoconverter_parentpicker').remove();
}

function populate_project_dropdown()
{
    var comm = $('#id_picker_commission_dropdown').val();
    var mine = $('#id_picker_mine_only').is(":checked");

    $('#id_picker_project_dropdown').empty();
    $('#plutoconverter_picker_throbber').fadeIn();
    $('#plutoconverter_picker_save_button').hide();

    $.getJSON('/portal.plugins.gnmplutoconverter/projects?comm=' + comm + '&mine=' + mine).success(function(data, jqXHR){
        $.each(data, function(idx,ptr){
            $('#id_picker_project_dropdown').append(
                $('<option>', {'value': ptr['vsid']}).html(ptr['title'])
            );
        });
        $('#plutoconverter_picker_throbber').fadeOut();
        $('#plutoconverter_picker_save_button').show();
    }).fail(function(jqXHR, errorThrown, status){
        $('#plutoconverter_parentpicker_error').html(errorThrown + '; ' + status);
        console.log("AJAX commission query failed");
    });
}

function populate_commission_dropdown()
{
    var wg = $('#id_picker_workinggroup_dropdown').val();
    var mine = $('#id_picker_mine_only').is(":checked");

    $('#id_picker_commission_dropdown').empty();
    $('#id_picker_project_dropdown').empty();

    $('#plutoconverter_picker_throbber').fadeIn();
    $('#plutoconverter_picker_save_button').hide();

    $.getJSON('/portal.plugins.gnmplutoconverter/commissions?wg=' + wg + '&mine=' + mine).success(function(data, jqXHR){
        $.each(data, function(idx,ptr){
            $('#id_picker_commission_dropdown').append(
                $('<option>', {'value': ptr['vsid']}).html(ptr['title'])
            );
        });
        $('#plutoconverter_picker_throbber').fadeOut();
        $('#plutoconverter_picker_save_button').show();
        populate_project_dropdown();
    }).fail(function(jqXHR, errorThrown, status){
        $('#plutoconverter_parentpicker_error').html(errorThrown + '; ' + status);
        console.log("AJAX commission query failed");
    });
}

function plutoconverter_picker_save()
{
    console.log("Selected commission: " + $('#id_picker_commission_dropdown').val());
    console.log("Selected project: " + $('#id_picker_project_dropdown').val());
    $('#plutoconverter_project_id_input').val($('#id_picker_project_dropdown').val());
    $('#plutoconverter_commission_id_input').val($('#id_picker_commission_dropdown').val());
    $('#plutoconverter_item_project_error').empty();
    $('#plutoconverter_item_commission_error').empty();

    $('#plutoconverter_parentpicker').dialog("close");
    $('#plutoconverter_parentpicker').remove();
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
    var mine_only_checkbox = $('<input>', {'type': 'checkbox', 'checked': true, 'id': 'id_picker_mine_only'}).appendTo(i);
    mine_only_checkbox.change(populate_commission_dropdown);
    $('<label>', {'for': 'id_picker_mine_only'}).html('Only show commissions belonging to me').appendTo(i);


    var i = $('<li>').appendTo(lst);
    var wd_drop = $('<select>', {'id': 'id_picker_workinggroup_dropdown'}).appendTo(i);
    $('<label>', {'for': 'id_picker_workinggroup_dropdown'}).html('Working group').appendTo(i);
    wd_drop.change(populate_commission_dropdown);

    $.getJSON('/portal.plugins.gnmplutoconverter/workinggroups?mine=' + $('#id_picker_mine_only').val()).success(function(data, jqXHR){
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
    commission_drop.change(populate_project_dropdown);

    var i = $('<li>').appendTo(lst);
    var project_drop = $('<select>', {'id': 'id_picker_project_dropdown'}).appendTo(i);
    $('<label>', {'for': 'id_picker_project_dropdown'}).html('Project').appendTo(i);

    var i = $('<li>').appendTo(lst);
    var item_span = $('<span>').appendTo(i)
    var save_button = $('<button>', {'type': 'button', 'id': 'plutoconverter_picker_save_button'}).html("Choose").click(plutoconverter_picker_save).appendTo(item_span);
    var throbber_image = $('<img>', {'src': '/sitemedia/img/core/loading-small.gif',
                                     'style': 'width: 16px;',
                                      'id': 'plutoconverter_picker_throbber'
                                      }).appendTo(item_span);
    throbber_image.hide();

}

function close_dialog()
{
    $('#plutoconverter_dlg').dialog("close");
}

function showCompletedMessage(itemid)
{
    $('#id_error_text').empty();

    $('<p>', {'style': 'font-size: 1.4em; color: green;float: left;'}).text('Conversion succeeded!').appendTo($('#id_error_text'));

    $('<a>', {'href': '#',
              'onClick': 'close_dialog();',
              'class': "blue-button button mark not-bold",
              'style': "color: white; float: right; margin-right:10px;"
             }).text('Close').appendTo($('#id_error_text'));

    $('<a>', {'href': "/master/"+ itemid,
              'onClick': 'close_dialog();',
              'class': "blue-button button mark not-bold",
              'style': "color: white; float: right; margin-right:10px;"
             }).text('View Master').appendTo($('#id_error_text'));
}

function build_dialog()
{
    var global_font_size = '1.6em'; //horrible i know but will work for time being
    var dlg=$('<div>', {'id': 'plutoconverter_dlg', 'style': 'display: none;', 'title': 'Convert to Pluto master'});

    var form = $('<form>', {'method': 'POST', 'id': 'plutoconverter_mainform'}).appendTo(dlg);

    var content_table = $('<table>').appendTo(form);

    var tr_item = $('<tr>').appendTo(content_table);
    $('<td>',{'style': 'text-align: right;'}).html('I would like to attach item: ').appendTo(tr_item);

    $('<input>', {'id': 'plutoconverter_item_id_input', 'name': 'plutoconverter_item_id_input', 'type': 'text', 'disabled': false}).appendTo(
        $('<td>',{'id': 'plutoconverter_item_id_label','font-size': global_font_size})
    ).appendTo(tr_item);

    var tr_project = $('<tr>').appendTo(content_table);
    $('<td>',{'style': 'text-align: right;'}).html('To the project: ').appendTo(tr_project);

    var td_selector = $('<td>',{'id': 'plutoconverter_item_project_label','font-size': global_font_size}).appendTo(tr_project);
    var input = $('<input>', {'id': 'plutoconverter_project_id_input', 'name': 'plutoconverter_project_id_input', 'disabled': false}).appendTo(td_selector);
    $('<a>', {'href': '#', 'onclick': 'open_picker("project");'}).html("Choose...").appendTo(td_selector);
    $('<br>').appendTo(td_selector);
    $('<p>', {'id': 'plutoconverter_item_project_error', 'class': 'error'}).appendTo(td_selector);
    input.change(function(){
        $('#plutoconverter_item_project_error').empty();
    })

    var tr_commission = $('<tr>').appendTo(content_table);
    $('<td>',{'style': 'text-align: right;'}).html('within the commission: ').appendTo(tr_commission);

    var td_selector = $('<td>',{'id': 'plutoconverter_item_commission_label','font-size': global_font_size}).appendTo(tr_commission);

    var input = $('<input>', {'id': 'plutoconverter_commission_id_input', 'name': 'plutoconverter_commission_id_input', 'disabled': false}).appendTo(td_selector);
    $('<br>').appendTo(td_selector);
    $('<p>', {'id': 'plutoconverter_item_commission_error', 'class': 'error'}).appendTo(td_selector);
    input.change(function(){
        $('#plutoconverter_item_commission_error').empty();
    })

    var tr_submit = $('<tr>').appendTo(content_table);
    var td_submit = $('<td>').appendTo(tr_submit);
    $('<input>', {'type': 'submit'}).html('Convert').appendTo(td_submit);
    var throbber = $('<img>', {'src': '/sitemedia/img/core/loading-small.gif', 'style': 'width: 16px;', 'id': 'plutoconverter_throbber'}).appendTo(td_submit);
    throbber.hide();
    var error_text = $('<p>', {'class': 'error', 'id': 'id_error_text'}).appendTo(form);

    form.submit(function(event){
        event.preventDefault(); //prevent the browser to do normal submission
        var is_vsid = /^\w{2}-\d+$/;
        if(!is_vsid){
            alert("unable to build regex");
            return;
        }

        //var data = ;
        var validated=true;

        if(! is_vsid.test($('#plutoconverter_project_id_input').val())){
            $('#plutoconverter_item_project_error').html("This is not a valid Vidispine ID");
            validated = false;
        }
        if(! is_vsid.test($('#plutoconverter_commission_id_input').val())){
            $('#plutoconverter_item_commission_error').html("This is not a valid Vidispine ID");
            validated = false;
        }
        if(!validated) return;

        throbber.fadeIn();
        error_text.html("Performing conversion...");

        console.log($('#plutoconverter_mainform').serialize());
        $.ajax({
            type: "POST",
            url: "/portal.plugins.gnmplutoconverter/do_conversion",
            data: $('#plutoconverter_mainform').serialize()
        }).success(function(data){
            throbber.fadeOut();
            td_submit.hide();
            console.log(data);
            showCompletedMessage(data['itemid']);
            //$('#plutoconverter_dlg').dialog("close");
        }).fail(function(jqXHR, errorThrown, status){
            throbber.fadeOut();
            try{
                error_info = jQuery.parseJSON(jqXHR.responseText);
                error_text.html(error_info['error']);
            } catch(err){   //unable to get a json object
                error_text.html("Unable to convert: " + errorThrown + "; " + status);
            };
        });

    });

    $(document.body).append(dlg);
}

$(document).ready(function(){
    build_dialog();
    $('#plutoconverter_dlg').dialog({
        autoOpen: false,
        width: 600,
    });
});