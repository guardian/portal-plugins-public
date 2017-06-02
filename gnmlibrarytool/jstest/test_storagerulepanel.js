var should = require('should'),
    expect = require('expect'),
    assert = require('assert'),
    jsdom = require('node-jsdom');
var sinon = require('sinon');
var fs = require('fs');

var js_under_test = fs.readFileSync(__dirname + '/../static/gnmlibrarytool/js/storagerulepanel.js');
var jquery = fs.readFileSync(__dirname + "/lib/jquery.js");

describe("storagerulepanel.js", function(){
    describe("load_storagerule_info", function(){
        var html = '<html><body><p class="mvlibtool_error" id="mvlibtool_error"> </p> <span id="mvlibtool_sr_loading"> <span>Loading...</span> </span>'+
            '<form action="/gnmlibrarytool/item/delete/" method="post"> <input type="hidden" name="itemid" value="{{ item_id }}">' +
            '<table id="mvlibtool_sr_info"> </table> </form></body></html>';
        it("should request ajax info from server and render it to page", function(done){
            var data = [
                {
                    shapetag: 'original',
                    rules: [
                        {
                            storages: [
                                'VX-4',
                                'VX-5',
                                'VX-6'
                            ],
                            not_storages: [],
                            groups: [],
                            not_groups: [],
                            storage_count: 3,
                            applies_to: ['LIBRARY', 'VX*345']
                        }
                    ]
                }
            ];
            jsdom.env({
                html: html,
                documentRoot: __dirname + "/lib",
                src: [
                    jquery.toString(),
                    js_under_test.toString()
                ],
                done: function (error, window) {
                    window.console = console;
                    if (error) {
                        console.error(error);
                        return;
                    }
                    var $ = window.jQuery;

                    var callback = sinon.spy();
                    // Creating a deffered object
                    var dfd = $.Deferred();

                    window.itemPlayer = {
                        playerResize: sinon.spy()
                    };

                    // Stubbing the ajax method
                    sinon.stub($, 'ajax').callsFake(function (url, options) {
                        // assigns success callback to done.
                        if (options.success) dfd.done([
                                function () {
                                    options.success(data);
                                    options.always();
                                },
                                function () {
                                    /*now that the success callback has been triggered, test that it had the right effects*/
                                    var mvlibtool_sr_info = $("#mvlibtool_sr_info");
                                    var paras = mvlibtool_sr_info.find('p');
                                    expect(paras.length).toEqual(2);   //should get two paras; one for rules and one for applies to

                                    expect(mvlibtool_sr_info.find('.shapetag-container').html()).toEqual("original");

                                    var rulesContainer = mvlibtool_sr_info.find('.rule-container');
                                    expect(rulesContainer.text()).toEqual("Minimum copies: 3.  Include: VX-4,VX-5,VX-6,; Exclude: (none)");

                                    var appliesContainer = mvlibtool_sr_info.find('.applies-container');
                                    expect(appliesContainer.text()).toEqual("Applied from LIBRARY VX*345");

                                    assert($('#mvlibtool_sr_loading').not(":visible"));
                                    done();
                                }
                            ]
                        );

                        // assigns error callback to fail.
                        if (options.error) dfd.fail(options.error);
                        dfd.success = dfd.done;
                        dfd.error = dfd.fail;

                        // returning the deferred object so that we can chain it.
                        return dfd;
                    });

                    window.load_storage_rule_info('VX-374');
                    assert($('#mvlibtool_sr_loading').is(":visible"));

                    assert(window.itemPlayer.playerResize.calledOnce);
                    expect(window.itemPlayer.playerResize.getCall(0).args[0]).toEqual("small");

                    assert($.ajax.calledOnce);
                    assert($.ajax.calledWith('/gnmlibrarytool/storageruleinfo/VX-374'));


                    dfd.resolve();
                }
            });
        });
        it("should show a message if no shapes are present", function(done){
            var data = [
            ];
            jsdom.env({
                html: html,
                documentRoot: __dirname + "/lib",
                src: [
                    jquery.toString(),
                    js_under_test.toString()
                ],
                done: function (error, window) {
                    window.console = console;
                    if (error) {
                        console.error(error);
                        return;
                    }
                    var $ = window.jQuery;

                    var callback = sinon.spy();
                    // Creating a deffered object
                    var dfd = $.Deferred();

                    window.itemPlayer = {
                        playerResize: sinon.spy()
                    };

                    // Stubbing the ajax method
                    sinon.stub($, 'ajax').callsFake(function (url, options) {
                        // assigns success callback to done.
                        if (options.success) dfd.done([
                                function () {
                                    options.success(data);
                                    options.always();
                                },
                                function () {
                                    /*now that the success callback has been triggered, test that it had the right effects*/
                                    expect($('#mvlibtool_error').text()).toEqual("No shapes were found on this item");

                                    assert($('#mvlibtool_sr_loading').not(":visible"));
                                    done();
                                }
                            ]
                        );

                        // assigns error callback to fail.
                        if (options.error) dfd.fail(options.error);
                        dfd.success = dfd.done;
                        dfd.error = dfd.fail;

                        // returning the deferred object so that we can chain it.
                        return dfd;
                    });

                    window.load_storage_rule_info('VX-374');
                    assert($('#mvlibtool_sr_loading').is(":visible"));

                    assert(window.itemPlayer.playerResize.calledOnce);
                    expect(window.itemPlayer.playerResize.getCall(0).args[0]).toEqual("small");

                    assert($.ajax.calledOnce);
                    assert($.ajax.calledWith('/gnmlibrarytool/storageruleinfo/VX-374'));


                    dfd.resolve();
                }
            });
        });
        it("should show an error message sent by the server", function(done){
            var data = {
                status: 'error',
                error: 'My hovercraft is full of eels'
            };

            jsdom.env({
                html: html,
                documentRoot: __dirname + "/lib",
                src: [
                    jquery.toString(),
                    js_under_test.toString()
                ],
                done: function (error, window) {
                    window.console = console;
                    if (error) {
                        console.error(error);
                        return;
                    }
                    var $ = window.jQuery;

                    var callback = sinon.spy();
                    // Creating a deffered object
                    var dfd = $.Deferred();

                    window.itemPlayer = {
                        playerResize: sinon.spy()
                    };

                    // Stubbing the ajax method
                    sinon.stub($, 'ajax').callsFake(function (url, options) {
                        // assigns success callback to done.
                        if (options.success) dfd.done([
                                function () {
                                    options.success(data);
                                    options.always();
                                },
                                function () {
                                    /*now that the success callback has been triggered, test that it had the right effects*/
                                    expect($('#mvlibtool_error').text()).toEqual("A server error occurred: My hovercraft is full of eels");

                                    assert($('#mvlibtool_sr_loading').not(":visible"));
                                    done();
                                }
                            ]
                        );

                        // assigns error callback to fail.
                        if (options.error) dfd.fail(options.error);
                        dfd.success = dfd.done;
                        dfd.error = dfd.fail;

                        // returning the deferred object so that we can chain it.
                        return dfd;
                    });

                    window.load_storage_rule_info('VX-374');
                    assert($('#mvlibtool_sr_loading').is(":visible"));

                    assert(window.itemPlayer.playerResize.calledOnce);
                    expect(window.itemPlayer.playerResize.getCall(0).args[0]).toEqual("small");

                    assert($.ajax.calledOnce);
                    assert($.ajax.calledWith('/gnmlibrarytool/storageruleinfo/VX-374'));

                    dfd.resolve();
                }
            });
        });
    });
});