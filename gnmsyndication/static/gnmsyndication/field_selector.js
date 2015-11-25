var target_field_id="";

function fill_group_selector()
{
    $('#thrb_field_selector').show();
    $.getJSON('/gnmpurgemeister/info/groups',function(data,textStatus,jqXHR ){
        //console.log(data);

        $.each(data,function(idx,ptr){
            el = $('<option>', {'value': ptr });
            el.html(ptr);
            $('#field_group_selector').append(el);
        });

        fill_fieldname_selector(data[0]);
    }).always(function(){
        $('#thrb_field_selector').hide();
    });

}

function field_group_selector_changed()
{
    console.log($('#field_group_selector').val());
    fill_fieldname_selector($('#field_group_selector').val());
}

function fill_fieldname_selector(value)
{
    $('#field_name_selector').empty();
    $('#thrb_field_selector').show();
    $.getJSON('/gnmpurgemeister/info/groups/' + value, function(data,textStatus,jqXHR){
        console.log(data);

        $.each(data, function(idx,ptr){
            el = $('<option>', {'value': ptr['internal_name'], 'data_widget': ptr['widget'] });
            el.html(ptr['name']);
            $('#field_name_selector').append(el);
        });
        field_name_selector_changed();
    }).always(function(){
        $('#thrb_field_selector').hide();
    });
}

function widget_for_fieldtype(t, field_def)
{

if(t=='string-exact'){
    parent = $('<select>', {'id': 'id_value_entry', 'width': '90%'});
    $.each(field_def['values'], function(idx, ptr){
        el = $('<option>', {'value': ptr['key'] });
        el.html(ptr['value']);
        parent.append(el);
    });
    return parent;
} else {
    el = $('<input>', {'id': 'id_value_entry', 'width': '80%' });
    /* use jqueryui autocomplete from a list of potential terms */
    el.autocomplete({
        source: '/gnmpurgemeister/autocomplete/' + field_def['name']
    });
    return el;
}

}
function field_name_selector_changed()
{
    value = $('#field_name_selector').val();
    console.log(value);
    $('#field_value_input').empty();
    $('#thrb_field_selector').show();

    $.getJSON('/gnmpurgemeister/info/fields/' + value, function(data, textStatus, jqXHR){
        console.log(data);
        $('#field_value_input').append(widget_for_fieldtype(data['type'], data));
        b = $('<button>', {'id': 'field_entry_button', 'type': 'button', 'onclick': 'field_entry_button_clicked();' });
        b.html("Add condition");
        $('#field_value_input').append(b);
    }).always(function(){
        $('#thrb_field_selector').hide();
    });

}

function field_entry_button_clicked()
{
    field = $('#field_name_selector').val();

    alert('You selected '+field+'.');

    $(target_field_id).val(field);
    $('#field_selector_dialog').dialog("close");
}

function show_field_selector(target_field)
{
    target_field_id=target_field;
    $('#field_selector_dialog').dialog("open");
}

function hide_field_selector()
{
alert('hide_field_selector!');
    $('#field_selector_dialog').dialog("close");
}

$(document).ready(function(){
    dlg = $('#field_selector_dialog').dialog({
        'autoOpen': false,
        closeOnEscape: true
    });
    $('#thrb_field_selector').hide();
    fill_group_selector();
});