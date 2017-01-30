function restoring_message()
//builds a DOM fragment to issue a holding message
{
    return
        $("<img>", {'src': '/sitemedia/img/loading.gif'}).append(
            $("<p>", {'text': 'Requesting restore, please wait...'})
        );
}

function get_stats(response_list)
{
    return response_list.reduce(function(accumulator, currentValue, currentIndex, array){
                if(currentValue['status']=="ok") accumulator['status_ok']+=1;
                if(currentValue['task_id']!=null) accumulator['with_task']+=1;
                return accumulator;
            }, {'with_task':0, 'status_ok': 0, 'count': response_list.length});
}

function request_restore(endpoint, objectClassName, jqDialogObject)
{
    jqDialogObject.empty();
    jqDialogObject.html(restoring_message());

    $.ajax(endpoint).complete(function(data){
        if(data.hasOwnProperty('count')){   //we've done a batch restore
            var stats = get_stats(data['responses']);
        } else {
            var stats = get_stats([data]);
        }

        console.log(stats);
        jqDialogObject.empty();
        jqDialogObject.append($("<p>", {'text': "Restore of " + stats['with_task'] + " item(s) in progress, out of "+ stats['count'] + " requested."}));
        jqDialogObject.append($("<p>", {'text': (stats['count'] - stats['ok']) + " items had errors."}));

    }).fail(function(jqXHR, errorThrown, detail){
        console.error("request_restore problem: " + errorThrown + " " + detail);
        console.error(jqXHR.body);
        jqDialogObject.empty();
        jqDialogObject.html($("<p>", {'class': 'error', 'text': errorThrown}));
    }).always(function(){

    });
}