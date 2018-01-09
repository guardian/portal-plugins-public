describe("check_link_status", function(){
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

    it("should make an ajax query for the status of each link that's not Available or Failed", function(){
        var linkentries = $(".sharable-link-entry");
        var promise_list = check_link_status(false);

        expect($.ajax.callCount).to.equal(3);

        try {
            expect($.ajax.calledWith("/gnmdownloadablelink/api/link/1")).to.equal(true);
            expect($.ajax.calledWith("/gnmdownloadablelink/api/link/2")).to.equal(true);
            expect($.ajax.calledWith("/gnmdownloadablelink/api/link/3")).to.equal(true);
        }catch(e){
            console.log($.ajax.getCall(0).args);
            console.log($.ajax.getCall(1).args);
            console.log($.ajax.getCall(2).args);
            throw e;
        }

        promise_list[0].resolve({
            expiry: '2018-02-01T00:00:00Z',
            status: 'Available',
            public_url: 'http://some/url/to/file.ext',
            shapetag: 'mezzanine'
        });
        expect(linkentries.eq(0).attr('data-entrystatus')).to.equal('Available');
        expect(linkentries.eq(0).text()).to.equal('mezzanine Available until February 1st 2018, 12:00:00 am Download');
        expect(linkentries.eq(0).find('a').attr('href')).to.equal('http://some/url/to/file.ext');

        promise_list[1].resolve({
            expiry: '2018-02-01T00:00:00Z',
            status: 'Failed',
            shapetag: 'lowres'
        });
        expect(linkentries.eq(1).attr('data-entrystatus')).to.equal('Failed');
        expect(linkentries.eq(1).text()).to.equal('lowres Failed');
        expect(linkentries.eq(1).find('a').length).to.equal(0);

        promise_list[2].resolve({
            expiry: '2018-02-01T00:00:00Z',
            status: 'Transcoding',
            shapetag: 'lowaudio'
        });
        expect(linkentries.eq(2).attr('data-entrystatus')).to.equal('Transcoding');
        expect(linkentries.eq(2).text()).to.equal('lowaudio Transcoding');
        expect(linkentries.eq(2).find('a').length).to.equal(0);
    });

});