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
        var fake_now_time = new Date(2018,0,18,9,37,56,0);
        console.log(fake_now_time);
        var promise_list = check_link_status(false, fake_now_time);

        expect($.ajax.callCount).to.equal(3);

        try {
            expect($.ajax.calledWith("/gnmdownloadablelink/api/link/1")).to.equal(true);
            expect($.ajax.calledWith("/gnmdownloadablelink/api/link/2")).to.equal(true);
            expect($.ajax.calledWith("/gnmdownloadablelink/api/link/3")).to.equal(true);
        }catch(e){
            console.error($.ajax.getCall(0).args);
            console.error($.ajax.getCall(1).args);
            console.error($.ajax.getCall(2).args);
            throw e;
        }

        promise_list[0].resolve({
            expiry: '2018-02-01T00:00:00Z',
            status: 'Available',
            public_url: 'http://some/url/to/file.ext',
            shapetag: 'mezzanine'
        });
        expect(linkentries.eq(0).attr('data-entrystatus')).to.equal('Available');
        //expect(linkentries.eq(0).text()).to.equal('mezzanine Available until February 1st 2018, 12:00:00 am Copy me and paste into an email');
        console.log(linkentries.eq(0));
        console.log(linkentries.eq(0).find('span.link-avail-until'));
        expect(linkentries.eq(0).find('span.link-status').text()).to.equal("Available for 14 days 2 hours");
        expect(linkentries.eq(0).find('span.link-status').hasClass("link-expires-soon")).to.equal(false);
        expect(linkentries.eq(0).find('span.link-shape-name').text()).to.equal("mezzanine");
        expect(linkentries.eq(0).find('a.download-link').attr('href')).to.equal('http://some/url/to/file.ext');

        promise_list[1].resolve({
            expiry: '2018-02-01T00:00:00Z',
            status: 'Failed',
            shapetag: 'lowres'
        });
        expect(linkentries.eq(1).attr('data-entrystatus')).to.equal('Failed');
        expect(linkentries.eq(1).find('span.link-shape-name').text()).to.equal("lowres");
        expect(linkentries.eq(1).find('span.link-status').text()).to.equal('Failed');
        expect(linkentries.eq(1).find('a.retry-button').length).to.equal(1);

        promise_list[2].resolve({
            expiry: '2018-02-01T00:00:00Z',
            status: 'Transcoding',
            shapetag: 'lowaudio'
        });
        expect(linkentries.eq(2).attr('data-entrystatus')).to.equal('Transcoding');
        expect(linkentries.eq(2).find('span.link-shape-name').text()).to.equal("lowaudio");
        expect(linkentries.eq(2).find('span.link-status').text()).to.equal('Transcoding');
        expect(linkentries.eq(2).find('a').length).to.equal(0);
    });

    it("should set a css class to highlight any link that is expiring soon", function(){
        var linkentries = $(".sharable-link-entry");
        var fake_now_time = new Date(2018,0,31,9,37,56,0);
        console.log(fake_now_time);
        var promise_list = check_link_status(false, fake_now_time);

        expect($.ajax.callCount).to.equal(1);

        try {
            expect($.ajax.calledWith("/gnmdownloadablelink/api/link/3")).to.equal(true);
        }catch(e){
            console.error($.ajax.getCall(0).args);
            throw e;
        }

        console.log(promise_list.length);

        promise_list[0].resolve({
            expiry: '2018-02-01T00:00:00Z',
            status: 'Available',
            public_url: 'http://some/url/to/file.ext',
            shapetag: 'lowaudio'
        });

        // for(var n=0;n<3;++n){
        //     console.log(n + ": " + linkentries.eq(n).attr('data-entrystatus'));
        //     console.log(n + ": " + linkentries.eq(n).find('span.link-status').text());
        //     console.log(n + ": " + linkentries.eq(n).find('span.link-shape-name').text());
        // }
        expect(linkentries.eq(2).attr('data-entrystatus')).to.equal('Available');

        expect(linkentries.eq(2).find('span.link-status').text()).to.equal("Available for 1 days 2 hours");
        expect(linkentries.eq(2).find('span.link-status').hasClass("link-expires-soon")).to.equal(true);
        expect(linkentries.eq(2).find('span.link-shape-name').text()).to.equal("lowaudio");
        expect(linkentries.eq(2).find('a.download-link').attr('href')).to.equal('http://some/url/to/file.ext');
    });
});