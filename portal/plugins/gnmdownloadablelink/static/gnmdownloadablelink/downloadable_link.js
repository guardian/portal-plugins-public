function downloadablelink_populate_shapelist() {
    $('#downloadable-link-shape-list').empty();
    return $.ajax("/gnmdownloadablelink/api/shapetags")
        .done(function(data, jqXHR){

            $.each(data.uri, function(idx,ptr){
                var element = $('<input>',{
                    type: 'radio',
                    class: 'downloadable-link-control downloadable-link-shapetag-group',
                    name: 'downloadable-link-shapetag',
                    value: ptr,
                    selected: idx===0
                });

                var label = $('<span>').text(ptr);
                var item = $('<li>',{style: 'list-style: none'});
                item.append(element);
                item.append(label);

                $('#downloadable-link-shape-list').append(item);
            });
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

/* called when the 'create' button is clicked from the dialog */
function downloadablelink_create(created_time){
    var datestring = $('#downloadable-link-expiry-time-date').val() + " " + $('#downloadable-link-expiry-time-hours').val() + ":" + $('#downloadable-link-expiry-time-mins').val();

    var shapetag = get_current_shapetag();
    if(created_time===undefined) created_time = new Date();
    var formdata = {
        status: "Requested",
        created: created_time.toISOString(),
        expiry: new Date(datestring).toISOString()
    };

    var postdata = JSON.stringify(formdata);
    console.log(postdata);

    var url = "/gnmdownloadablelink/api/new/" + $('#downloadable-link-itemid').val() + "/" + shapetag;

    return $.ajax(url, {type: "POST", data: postdata, contentType: 'application/json'})
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

/* called when the 'retry' link is clicked from the pluginblock */
function downloadablelink_retry(link_id){
    var url = "/gnmdownloadablelink/api/retry/" + link_id;

    $('li[data-entryid="' + link_id + '"]').attr('data-entrystatus',"Retrying");
    return $.ajax(url, {type: "POST", data: {}, contentType: 'application/json'})
        .done(function(data,jqXHR) {
            $('#downloadable-link-errormsg').html("Successfully requested retry");
            $('i#retry-button-' + link_id).fadeOut(400, function(){
                $('i#retry-tick-' + link_id).fadeIn(400);
            });
        })
        .fail(function(jqXHR, desc, errorThrown){
            /*show an error icon, and replace the button 5 seconds later*/
            $('i#retry-button-' + link_id).fadeOut(400, function(){
                $('i#retry-fail-' + link_id).fadeIn(400);
            });
            window.setTimeout(function(){
                $('i#retry-fail-' + link_id).fadeOut(400, function(){
                    $('i#retry-button-' + link_id).fadeIn(400);
                });
            },5000);
            console.error(jqXHR);
        })
}

/* called when the 'close' button is clicked on the dialog */
function downloadablelink_close() {
    $('#downloadable-link-create-dlg').dialog("close");
}

/* Generates the html for a 'retry' link */
function make_retry_link(entryid, parent_elem){
    /* create a retry button */
    return $('<a>',{onClick: 'downloadablelink_retry("' + entryid + '")',
        onMouseOver: "$(this).css('background-color', '#BBBBBB')",
        onMouseOut: "$(this).css('background-color', '')",
        class: 'retry-button',
        title: 'Retry creating failed link',
        style: 'margin-left: 0.4em; height:8px; cursor: pointer; border-radius: 25px; padding: -12px'}
    ).append($('<i>',{class: 'fa fa-refresh', id: 'retry-button-' + entryid })
    ).append($('<i>', {class: 'fa fa-check', id: 'retry-tick-' + entryid, title: 'Retry requested', style: 'color: green; display: none'})
    ).append($('<i>', {class: 'fa fa-exclamation-circle', id: 'retry-fail-' + entryid, title: 'Request failed', style: 'color: red; display: none'}));
}

var one_day = 24*3600*1000;

/*called regularly from window.setTimer to update link status entries*/
function check_link_status(initial){

    return $(".sharable-link-entry").map(function(idx,ptr){
        var elem = $(ptr);

        var entrystatus = elem.attr("data-entrystatus");
        var entryid = elem.attr("data-entryid");


        if(initial || (entrystatus!=="Available" && entrystatus!=="Failed")){
            return $.ajax("/gnmdownloadablelink/api/link/" + entryid)
                .done(function(data, jqXHR){
                    var statusstring;
                    var statusElem;
                    var labelClass = "link-status";
                    if(data.status==="Available"){
                        console.log("expiry date: " + data.expiry);
                        var expiryMoment = moment(data.expiry);
                        console.log("expiry moment: " + expiryMoment.format('MMMM Do YYYY, h:mm:ss a'));

                        var expiryDiff = moment(expiryMoment.diff(moment(Date.now())));
                        console.log("now moment: " + moment(Date.now()).format('MMMM Do YYYY, h:mm:ss a'));
                        console.log("expiryDiff: " + expiryDiff);
                        console.log("compare: " + 1*one_day);
                        
                        if(expiryDiff < one_day ) labelClass = " link-expires-soon";

                        statusElem = $('<span>',{class: labelClass}).html("Available for " + expiryDiff.format('DD') + " days "+ expiryDiff.format('h') + " hours");
                    } else {
                        statusElem = $('<span>',{class: labelClass}).html(data.status);
                    }
                    var shapeElem = $('<span>',{id: data.shapetag + "_elem"}).html(data.shapetag);

                    elem.append(shapeElem);
                    elem.append(statusElem);
                    if(data.public_url){
                        elem.append(
                            $('<a>',{class: "download-link", href: data.public_url}).html("Copy me and paste into an email")
                                .append($('i', {class: "fa fa-link"}))
                        );
                    }
                    if(data.status==="Failed"){
                        elem.append(make_retry_link(entryid, elem));
                    }
                    elem.attr("data-entrystatus",data.status);
                })
                .fail(function(jqXHR, errorThrown){
                    elem.html("<p class=\"error\">Could not update: " + errorThrown + "</p>");
                });
        }
    });
}

function add_new_link(link_url){
    return $.ajax(link_url)
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