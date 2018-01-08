function downloadablelink_populate_shapelist() {
    $('#downloadable-link-shape-list').empty();
    $.ajax("/gnmdownloadablelink/api/shapetags")
        .done(function(data, jqXHR){
            $.each(data.uri, function(idx,ptr){
                var element = $('<input>',{type: 'radio', class: 'downloadable-link-control downloadable-link-shapetag-group', name: 'downloadable-link-shapetag', value: ptr, selected: idx===0});
                var label = $('<span>').text(ptr);
                var item = $('<li>',{style: 'list-style: none'});
                item.append(element);
                item.append(label);

                $('#downloadable-link-shape-list').append(item);
            })
        })
        .fail(function(jqXHR, errorThrown, errorDetail){
            $("#downloadable-link-errormsg").html("Could not get shape tag list: " + errorThrown);
        });
}

function downloadablelink_show() {
    downloadablelink_populate_shapelist();
    $('#downloadable-link-create-dlg').dialog("open");
}

function get_current_shapetag(){
    return $(".downloadable-link-shapetag-group:checked").val();
}

function downloadablelink_create(){
    // var formdata = $('.downloadable-link-control').serializeArray();
    // console.log(formdata);
    var datestring = $('#downloadable-link-expiry-time-date').val() + " " + $('#downloadable-link-expiry-time-hours').val() + ":" + $('#downloadable-link-expiry-time-mins').val();

    var formdata = {
        status: "Requested",
        created: new Date().toISOString(),
        expiry: new Date(datestring).toISOString()
    };

    var shapetag = get_current_shapetag();

    var postdata = $.toJSON(formdata);
    console.log(postdata);

    var url = "/gnmdownloadablelink/api/new/" + $('#downloadable-link-itemid').val() + "/" + shapetag;

    $.ajax(url, {type: "POST", data: postdata, contentType: 'application/json'})
        .done(function(data, jqXHR){
            console.log(data);
            $('#downloadable-link-errormsg').html("Successfully requested new link");
            add_new_link(data.link);
            window.setTimeout(function(){ $('#downloadable-link-create-dlg').dialog("close");}, 1000);
        })
        .fail(function(jqXHR, desc, errorThrown){
            $('#downloadable-link-errormsg').html("Could not request new link: "+ errorThrown);
        });
}

function downloadablelink_close() {
    $('#downloadable-link-create-dlg').dialog("close");
}

function check_link_status(initial){
    /*called regularly to update link status entries*/
    $(".sharable-link-entry").each(function(idx,ptr){
        var elem = $(ptr);

        var entrystatus = elem.attr("data-entrystatus");
        var entryid = elem.attr("data-entryid");

        if(!initial &&
            entrystatus!=="Available" && entrystatus!=="Failed"){

            $.ajax("/gnmdownloadablelink/api/link/" + entryid)
                .done(function(data, jqXHR){
                    var htmlstring = data.shapetag + " " + data.status;
                    if(data.public_url){
                        htmlstring = htmlstring + ' <a href="' + data.public_url + '">Download</a>';
                    }
                    elem.html(htmlstring);
                    elem.attr("data-entrystatus",data.status);
                })
                .fail(function(jqXHR, errorThrown){
                    elem.html("<p class=\"error\">Could not update: " + errorThrown + "</p>");
                });
        }
    });
}

function add_new_link(link_url){
    $.ajax(link_url)
        .done(function(data, jqXHR){
            console.log(link_url);
            var entry_id = link_url.split('/').slice(-1).pop();
            console.log(entry_id);
            var item=$("<li>", {class: "sharable-link-entry", "data-entrystatus": data.status, "data-entryid": entry_id});
            item.text(data.shapetag + ": " + data.status);
            $('#downloadable-link-sharelist').append(item);
        })
        .fail(function(jqXHR, status, errorThrown){
            console.error(errorThrown);
        })
}

$(document).ready(function(){
    window.setInterval(function(){ check_link_status(false)}, 3000);
    for(var c=0;c<24;c++){
        var params={name: c, value: c};
        if(c===20) params['selected'] = true;
        $('<option>', params).text(c).appendTo($('#downloadable-link-expiry-time-hours'));
    }
    for(var d=0; d<60; d+=5){
        var params={name: d, value: d};
        if(d===0) params['selected'] = true;
        $('<option>', params).text(d).appendTo($('#downloadable-link-expiry-time-mins'));
    }

    $('#downloadable-link-create-dlg').dialog({autoOpen: false});
    $('#downloadable-link-expiry-time-date').datepicker();

    check_link_status(true);
});