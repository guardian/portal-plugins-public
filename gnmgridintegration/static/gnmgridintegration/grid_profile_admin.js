function regex_test_string()
{
    var re = new RegExp($('#id_field_value_regex').val(),'i');
    console.log("Regex is " + re);

    var result = re.exec($('#id_test_string').val());
    console.log("Match result is " + result);

    if(result){
        var match_html = $('#id_test_string').val().slice(0,result.index);
        match_html += '<span class="matched">' + result[0] + '</span>';
        match_html += $('#id_test_string').val().slice(result.index+result[0].length);

        $('#test_result_area').empty();
        $('#test_result_area').append($('<div>', {'style': 'display: inline-block;'}).html('Result: Matched'));
        $('#test_result_area').append(
            $('<div>', {'style': 'display: inline-block; padding-left:1em'}).append(
                $('<span>', {'class': 'unmatched' }).html(match_html)
            )
        );
    } else {
        $('#test_result_area').empty();
        $('#test_result_area').append($('<p>').html('Result: Did not match'));
    }
}

