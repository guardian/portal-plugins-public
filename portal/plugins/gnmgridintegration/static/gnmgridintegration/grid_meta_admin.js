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

function expanderMouseOver(exp)
{
exp.setAttribute('src','/sitemedia/portal.plugins.gnmgridintegration/arrow_sel.svg');

}

function expanderMouseOut(exp)
{
exp.setAttribute('src','/sitemedia/portal.plugins.gnmgridintegration/arrow_unsel.svg');
}

var expanded = false;

function expanderClicked(exp)
{
if(expanded){
    $('#grid_info_area').fadeOut();
    expanded = false;
} else {
    $('#grid_info_area').fadeIn();
    expanded = true;
}
}

function test_itemid_changed(){
    var value = $('#id_test_itemid').val();

    parts = value.match(/http:\/\/.*\/(\w{2}-\d+)\/*$/);
    if(parts){
        value = parts.pop();
    }

    console.log("Getting info for item ID " + value);

    $('.item_container').remove();
    $('#testitem_error_message').remove();

    $('#testitem_loading').show();
    $.getJSON('test/' + value + '/iteminfo', function(data){
        console.log(data);
        var containerDiv = $('<div>', {'class': 'item_container'});
        var textDiv = $('<div>', {'class': 'item_meta_text'});

        var htmlstring = '<span style="font-size: 1.1em"><a target="_blank" href="/vs/item/' + escapeHtml(data.item) + '">'+ escapeHtml(data.item) + "</a></span><br>";
        htmlstring += 'Title: <strong>' + escapeHtml(data.metadata.title) + '</strong><br>';
        /*htmlstring += "GNM Type: " + data.metadata.gnm_type + '<br>';
        htmlstring += "Asset Category: " + data.metadata.gnm_asset_category + '<br>';
        */
        $.each(data.metadata, function(key,value){
            if(key=='representativeThumbnailNoAuth') return;
            if(key=='title') return;
            if(key=='gnm_grid_image_refs') return;
            htmlstring += escapeHtml(key) + ": " + escapeHtml(value) + "<br>";
        });

        var numGridImgs = 0;
        if(data.metadata.gnm_grid_image_refs!==null){
            if(Array.isArray(data.metadata.gnm_grid_image_refs)){
                numGridImgs = data.metadata.gnm_grid_image_refs.length;
            } else {
                numGridImgs = 1;
            }
        }

        htmlstring += "<hr>" + numGridImgs + " images already in the Grid";
        //htmlstring += "<br><button type=\"button\" onClicked=\"test_go_clicked('" + data['item'] + "');\">Test</button>";

        textDiv.html(htmlstring);
        textDiv.append($('<img>', {'class': 'simple_expander', 'onMouseOver': 'expanderMouseOver(this);',
                                   'onMouseOut': 'expanderMouseOut(this);', 'onClick': 'expanderClicked(this);',
                                   'src': '/sitemedia/portal.plugins.gnmgridintegration/arrow_unsel.svg'}));

        var gridInfo = $('<div>', {'id': 'grid_info_area', 'style': 'display: none;'});
        //var gridInfo = $('#grid_info_area');
        if(data.metadata.gnm_grid_image_refs!==null){
            $.each(data.metadata.gnm_grid_image_refs,function(idx,value){
                if(value!==null){
                    var fronturl = value.replace(/\/\/api\./,'//');
                    gridInfo.append($('<p>', {'class': 'grid_image_ref'}).html('<a href="' + fronturl + '" target="_blank">' + fronturl + '</a>'));
                }
            });
        }
        //textDiv.append(gridInfo);

        containerDiv.append($('<img>', {'class': 'item_meta_image', 'src': data.metadata.representativeThumbnailNoAuth}));
        $(containerDiv).append(textDiv);

        $(containerDiv).append($('<button>', {'type': 'button', 'onClick': 'test_go_clicked("' + data.item + '");'}).html('Test'));
        $(containerDiv).append(gridInfo);

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