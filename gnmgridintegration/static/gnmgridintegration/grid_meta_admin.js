function test_itemid_changed(){
    var value = $('#id_test_itemid').val();
    console.log("Getting info for item ID " + value);

    $.getJSON('test/' + value + '/iteminfo', function(data){
        console.log(data);
        var containerDiv = $('<div>', {'class': 'item_container'});
        var textDiv = $('<div>', {'class': 'item_meta_text'});

        var htmlstring = '<span style="font-size: 1.1em"><a target="_blank" href="/vs/item/' + data['item'] + '">'+ data['item'] + "</a></span><br>"
        htmlstring += 'Title: <strong>' + data['metadata']['title'] + '</strong><br>'
        /*htmlstring += "GNM Type: " + data['metadata']['gnm_type'] + '<br>'
        htmlstring += "Asset Category: " + data['metadata']['gnm_asset_category'] + '<br>'
        */
        $.each(data['metadata'], function(key,value){
            if(key=='representativeThumbnailNoAuth') return;
            if(key=='title') return;
            if(key=='gnm_grid_image_refs') return;
            htmlstring += key + ": " + value + "<br>";
        });

        htmlstring += "<br><button type=\"button\" onClicked=\"test_go_clicked('" + data['item'] + "');\">Test</button>";

        textDiv.html(htmlstring)
        containerDiv.append($('<img>', {'class': 'item_meta_image', 'src': data['metadata']['representativeThumbnailNoAuth']}))
        $(containerDiv).append(textDiv)
        $('#testitem').append(containerDiv);
    });
}