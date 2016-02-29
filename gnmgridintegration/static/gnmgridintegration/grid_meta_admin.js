var entityMap = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': '&quot;',
    "'": '&#39;',
    "/": '&#x2F;'
};

function escapeHtml(string) {
return String(string).replace(/[&<>"'\/]/g, function (s) {
    return entityMap[s];
});
}

function test_itemid_changed(){
    var value = $('#id_test_itemid').val();
    console.log("Getting info for item ID " + value);

    $('.item_container').remove();
    $('#testitem_error_message').remove();

    $('#testitem_loading').show();
    $.getJSON('test/' + value + '/iteminfo', function(data){
        console.log(data);
        var containerDiv = $('<div>', {'class': 'item_container'});
        var textDiv = $('<div>', {'class': 'item_meta_text'});

        var htmlstring = '<span style="font-size: 1.1em"><a target="_blank" href="/vs/item/' + escapeHtml(data['item']) + '">'+ escapeHtml(data['item']) + "</a></span><br>"
        htmlstring += 'Title: <strong>' + escapeHtml(data['metadata']['title']) + '</strong><br>'
        /*htmlstring += "GNM Type: " + data['metadata']['gnm_type'] + '<br>'
        htmlstring += "Asset Category: " + data['metadata']['gnm_asset_category'] + '<br>'
        */
        $.each(data['metadata'], function(key,value){
            if(key=='representativeThumbnailNoAuth') return;
            if(key=='title') return;
            if(key=='gnm_grid_image_refs') return;
            htmlstring += escapeHtml(key) + ": " + escapeHtml(value) + "<br>";
        });

        var numGridImgs = 0;
        if(Array.isArray(data['metadata']['gnm_grid_image_refs'])){
            numGridImgs = data['metadata']['gnm_grid_image_refs'].length;
        } else if(data['metadata']['gnm_grid_image_refs']!=null){
            numGridImgs = 1;
        }

        htmlstring += "<hr>" + numGridImgs + " images already in the Grid<br>";
        //htmlstring += "<br><button type=\"button\" onClicked=\"test_go_clicked('" + data['item'] + "');\">Test</button>";

        textDiv.html(htmlstring)
        containerDiv.append($('<img>', {'class': 'item_meta_image', 'src': data['metadata']['representativeThumbnailNoAuth']}))
        $(containerDiv).append(textDiv)

        $(containerDiv).append($('<button>', {'type': 'button', 'onClick': 'test_go_clicked("' + data['item'] + '");'}).html('Test'));

        $('#testitem_loading').hide();
        $('#testitem').append(containerDiv);
    }).fail(function(jqXHR, textStatus,errorDetail){
        $('#testitem_loading').hide();
        var errorText = $('<p>', {'class': 'error', 'id': 'testitem_error_message'});
        errorText.html('Unable to load item information: ' + errorDetail);
        $('#testitem').append(errorText);
    }).always(function(jqXHR){
        $('#testitem_loading').hide();
    });
}