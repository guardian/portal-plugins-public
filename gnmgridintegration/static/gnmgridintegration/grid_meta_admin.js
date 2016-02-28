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

function test_go_clicked(itemid)
{
    console.log("Testing Grid output for item ID " + itemid);

    $('.result_container').remove();
    $('#result_error_message').remove();
    $('#testresult_loading').show();

    $.getJSON('test/' + itemid, function(data){
        console.log(data);
        var containerDiv = $('<div>', {'class': 'result_container'});

        $.each(['item_meta','rights_meta'], function(idx,ptr){
            var container = $('<div>', {'id': ptr + '_container', 'class': 'result_data_panel'});
            container.append($('<span>', {'class': 'result_subheader'}).html(ptr));
            var dataTable = $('<table>', {'class': 'result_table'});
            $.each(data[ptr], function(idx, ent){
                var row = $('<tr>');
                row.append($('<td>', {'class': 'data_field_name'}).html(idx));
                row.append($('<td>', {'class': 'data_field_content'}).html(ent));
                dataTable.append(row);
            });
            container.append(dataTable);
            containerDiv.append(container);
        })

        $('#testresult_loading').hide();
        $('#testresults').append(containerDiv);
    }).fail(function(jqXHR, textStatus,errorDetail){
        $('#testresult_loading').hide();
        var errorText = $('<p>', {'class': 'error', 'id': 'testitem_error_message'});
        errorText.html('Unable to load item information: ' + errorDetail);
        $('#testresult').append(errorText);
    }).always(function(jqXHR){
        $('#testresult_loading').hide();
    });
}