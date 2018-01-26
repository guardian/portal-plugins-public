describe("downloadablelink_show", function(){
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
    });

    afterEach(function () {
        $.ajax.restore();
        //$.dialog.resetHistory();
    });

    it("should trigger an ajax download and show the dialog", function(){
        downloadablelink_show();
        expect($('#downloadable-link-create-dlg').dialog.calledWith("open")).to.equal(true);

        expect($.ajax.calledWith("/gnmdownloadablelink/api/shapetags")).to.equal(true);
    });

});

describe("downloadablelink_close", function(){
    it("should close the dialog", function(){
        downloadablelink_close();
        expect($('#downloadable-link-create-dlg').dialog.calledWith("close")).to.equal(true);

    });

});