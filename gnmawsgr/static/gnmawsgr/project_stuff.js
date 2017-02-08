function check_has_in_glacier(endpoint){
    //ask the server whether this project has any assets externally archived. If so, return true
    $("#gnmawsgr_loading_info").html("Checking how much of the project is in archive...");
    $.ajax(endpoint).done(function(data){
        console.log("received project info data: " + data);
        $("#glacier_restore_button_loading").hide();

        if(data.results.total_items>0){
            percentage_in_archive = (data.results.archived_items / data.results.total_items) *100;
        } else {
            percentage_in_archive = 0;
        }

        var lines = [
            "This project is " + percentage_in_archive.toFixed(0) + "% in deep archive (" + data.results.archived_items + "/" + data.results.total_items + " items)",
            data.results.restored_items + " have been restored and " + data.results.waiting_items + " are pending restore."
        ];

        $("#info_text").html(lines.join(" "));
        if(percentage_in_archive===0){
            console.log("project is not archived");
            $("#glacier_restore_button_container").hide();
        } else {
            $("#glacier_restore_button_container").fadeIn();
        }
    }).fail(function(jqXHR,errorThrown,detail){
        console.error("receiving project info: errorThrown");
        $("glacier_restore_button_loading").hide();
    });
}