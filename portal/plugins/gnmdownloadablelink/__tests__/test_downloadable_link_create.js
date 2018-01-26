describe("downloadablelink_create", function(){
    beforeEach(function(){
        //from http://blog.revathskumar.com/2013/03/testing-jquery-ajax-with-mocha-and-sinon.html
        this.callback = sinon.spy();

        // Stubbing the ajax method
        sinon.stub($, 'ajax').callsFake(function (options) {
            // Creating a deffered object
            var dfd = $.Deferred();

            // assigns success callback to done.
            if(options.success) dfd.done(function(argsone,argstwo){ options.success(argsone, argstwo) });

            // assigns error callback to fail.
            if(options.error) dfd.fail(options.error);
            dfd.success = dfd.done;
            dfd.error = dfd.fail;

            // returning the deferred object so that we can chain it.
            return dfd;
        });

        //set up the form as if it has been filled in
        $('#downloadable-link-expiry-time-date').val("03/04/2018");
        $('#downloadable-link-expiry-time-hours').val("20");
        $('#downloadable-link-expiry-time-mins').val("15");
        $('#downloadable-link-itemid').val("VX-352");

        var element = $('<input>',{
            type: 'radio',
            class: 'downloadable-link-control downloadable-link-shapetag-group',
            name: 'downloadable-link-shapetag',
            value: "my_shape",
            checked: true
        });

        var label = $('<span>').text("my_shape");
        var item = $('<li>',{style: 'list-style: none'});
        item.append(element);
        item.append(label);

        $('#downloadable-link-shape-list').append(item);

    });

    afterEach(function () {
        $.ajax.restore();
    });

    it("should be given currently selected shapetag by get_current_shapetag", function(){
        var result = get_current_shapetag();
        expect(result).to.equal("my_shape")
    });

    it("should marshal the form contents into json and submit via ajax", function(){
        var nowtime = new Date();
        downloadablelink_create(nowtime).resolve({status: 'ok', task_id: '211BD5C8-3F45-4351-916D-2E75308C3C55', link: '/api/link/21'});

        expect($.ajax.calledWith("/gnmdownloadablelink/api/new/VX-352/my_shape",{
            type: "POST",
            data: JSON.stringify({
                status: "Requested",
                created: nowtime.toISOString(),
                expiry: "2018-03-04T20:15:00.000Z"
            }),
            contentType: 'application/json'
        })).to.equal(true);

        expect($('#downloadable-link-errormsg').text()).to.equal("Successfully requested new link");

    });


    it("should show any submit errors in the error box", function(){
        var nowtime = new Date();
        /*FIXME: replace this placeholder with a more indicative server-side validation error in the fake jqXHR (arg 1)*/
        downloadablelink_create(nowtime).reject({}, 'error', 'Something bad happened');

        expect($.ajax.calledWith("/gnmdownloadablelink/api/new/VX-352/my_shape",{
            type: "POST",
            data: JSON.stringify({
                status: "Requested",
                created: nowtime.toISOString(),
                expiry: "2018-03-04T20:15:00.000Z"
            }),
            contentType: 'application/json'
        })).to.equal(true);

        expect($('#downloadable-link-errormsg').text()).to.equal("Could not request new link: Something bad happened");

    });
});