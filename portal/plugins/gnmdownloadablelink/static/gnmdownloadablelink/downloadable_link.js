function downloadablelink_create(){

}

function check_link_status(initial){
    /*called regularly to update link status entries*/
    $(".sharable-link-entry").each(function(idx,ptr){
        if(!initial &&
            ptr.attr("data-entrystatus")!=="Available" &&
            ptr.attr("data-entrystatus")!=="Failed"){

            $.ajax("/gnmdownloadablelink/api/link/" + ptr.attr("data-entryid"))
                .onComplete(function(data, jqXHR){
                    var htmlstring = data.shapetag + " " + data.status;
                    if(data.public_url){
                        htmlstring = htmlstring + '<a href="' + data.public_url + '">Download</a>';
                    }
                    ptr.html(htmlstring);
                })
                .onError(function(jqXHR, errorThrown){
                    ptr.html("<p class=\"error\">Could not update: " + errorThrown + "</p>");
                });
        }
    });
}

$(document).ready(function(){
    window.setTimeout(function(){ check_link_status(false)}, 3000);
    check_link_status(true);
});