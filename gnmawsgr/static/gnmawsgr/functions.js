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
    jqDialogObject.append(restoring_message());

    $.ajax(endpoint).done(function(data){
        if(data.hasOwnProperty('count')){   //we've done a batch restore
            var stats = get_stats(data['responses']);
        } else {
            var stats = get_stats([data]);
        }

        console.log(stats);
        //update the dialog box
        var interval_id = setInterval(function(){
            jqDialogObject.empty();
            jqDialogObject.append($("<p>", {'text': "Restore of " + stats['with_task'] + " item(s) in progress, out of "+ stats['count'] + " requested."}));
            jqDialogObject.append($("<p>", {'text': (stats['count'] - stats['ok']) + " items had errors."}));
        }, 3000);

    }).fail(function(jqXHR, errorThrown, detail){
        console.error("request_restore problem: " + errorThrown + " " + detail);
        console.error(jqXHR.body);
        jqDialogObject.empty();
        jqDialogObject.html($("<p>", {'class': 'error', 'text': errorThrown}));
    }).always(function(){

    });
}

function request_collection_restore(endpoint, updateEndpoint, objectClassName, jqDialogObject)
{
    jqDialogObject.empty();
    jqDialogObject.append(restoring_message());

    $.ajax(endpoint).done(function(data){
        console.log(data);
        jqDialogObject.append(
            $("<p>", {'text': "Bulk restore registered with ID of " + data['bulk_restore_request']})
        );


        //update the dialog box
        var interval_id = setInterval(function(){
            $.ajax(updateEndpoint).done(function(data){
                jqDialogObject.empty();
                jqDialogObject.append($("<h3>", {'text': "Restore of " + data['parent_collection'] + ": " + data['current_status']}));
                jqDialogObject.append($("<p>", {'text': "Restore of " + (data['number_queued']+data['number_already_going']) + " item(s) in progress, out of "+ data['number_requested'] + " requested."}));

                if(data['current_status']=="Failed"){
                    jqDialogObject.empty();
                    jqDialogObject.append($("<h3>", {'text': "Restore of " + data['parent_collection'] + ": " + data['current_status']}));
                    jqDialogObject.append($("<p>", {'text': "Failed with " + data['last_error']}));
                    clearInterval(interval_id);
                } else if(data['current_status']=="Completed"){
                    clearInterval(interval_id);
                }
            }).fail(function(jqXHR,errorThrown,detail){
                console.error("Unable to update bulk job status: " + errorThrown);
            });
        }, 3000);

    }).fail(function(jqXHR, errorThrown, detail){
        console.error("request_restore problem: " + errorThrown + " " + detail);
        console.error(jqXHR.body);
        jqDialogObject.empty();
        jqDialogObject.html($("<p>", {'class': 'error', 'text': errorThrown}));
    }).always(function(){

    });
}