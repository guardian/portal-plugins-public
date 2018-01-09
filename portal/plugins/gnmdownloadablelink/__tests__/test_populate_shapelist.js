describe("downloadablelink_populate_shapelist", function(){
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
    });

    it("should download shape tags", function(){
        var shapelist = $('#downloadable-link-shape-list');
        shapelist.empty();
        expect(shapelist.children().length).to.equal(0);

        downloadablelink_populate_shapelist().resolve({uri: ['shapetagone','shapetagtwo']});
        expect($.ajax.calledWith("/gnmdownloadablelink/api/shapetags"));
        expect(shapelist.children().length).to.equal(2);

        var entries = shapelist.children();

        expect(entries.eq(0).find('span').text()).to.equal("shapetagone");
        expect(entries.eq(1).find('span').text()).to.equal("shapetagtwo");
        expect($('#downloadable-link-errormsg').text()).to.equal("");
    });

    it("should log an error to the error box", function(){
        var shapelist = $('#downloadable-link-shape-list');
        shapelist.empty();
        expect(shapelist.children().length).to.equal(0);

        downloadablelink_populate_shapelist().reject({},"My hovercraft is full of eels");
        expect($.ajax.calledWith("/gnmdownloadablelink/api/shapetags"));
        expect($('#downloadable-link-errormsg').text()).to.equal("Could not get shape tag list: My hovercraft is full of eels");
        expect(shapelist.children().length).to.equal(0);
    });

});