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
            window.setTimeout(function(){ $('#downloadable-link-create-dlg').dialog("close");}, 1000);
        })
        .fail(function(jqXHR, desc, errorThrown){
            $('#downloadable-link-errormsg').html("Could not request new link: "+ errorThrown);
        });
    eventPreventDefault();
}

function downloadablelink_close() {
    $('#downloadable-link-create-dlg').dialog("close");
}

function check_link_status(initial){
    /*called regularly to update link status entries*/
    $(".sharable-link-entry").each(function(idx,ptr){
        if(!initial &&
            ptr.attr("data-entrystatus")!=="Available" &&
            ptr.attr("data-entrystatus")!=="Failed"){

            $.ajax("/gnmdownloadablelink/api/link/" + ptr.attr("data-entryid"))
                .done(function(data, jqXHR){
                    var htmlstring = data.shapetag + " " + data.status;
                    if(data.public_url){
                        htmlstring = htmlstring + '<a href="' + data.public_url + '">Download</a>';
                    }
                    ptr.html(htmlstring);
                })
                .fail(function(jqXHR, errorThrown){
                    ptr.html("<p class=\"error\">Could not update: " + errorThrown + "</p>");
                });
        }
    });
}

$(document).ready(function(){
    window.setTimeout(function(){ check_link_status(false)}, 3000);
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