import React from 'react';
import {shallow,mount} from 'enzyme';
import ErrorViewComponent from '../app/ErrorViewComponent.jsx';
import sinon from 'sinon';
import assert from 'assert';

describe("ErrorViewComponent", ()=>{
    it("should display an empty para if error object is null",()=>{
        const rendered = shallow(<ErrorViewComponent error={null}/>);
        expect(rendered.find('p.error-text').text()).toEqual("");
    });

    it("should direct user to the console log if there is a request but no response", ()=>{
        const fakeError ={
            request: {
                key: "value"
            }
        };

        console.error = sinon.spy();

        const rendered = shallow(<ErrorViewComponent error={fakeError}/>);
        expect(rendered.find('p.error-text').text()).toEqual("No response from server. See console log for more details.");
        assert(console.error.calledWith("Failed request: ", fakeError.request));
        console.error.reset();
    });

    it("should direct user to the console log if there is no request", ()=>{
        const fakeError = {
            message: "My hovercraft is full of eels"
        };

        console.error = sinon.spy();
        const rendered = shallow(<ErrorViewComponent error={fakeError}/>);
        expect(rendered.find('p.error-text').text()).toEqual("Unable to set up request. See console log for more details.");
        assert(console.error.calledWith('Axios error setting up request: ', fakeError.message));
        console.error.reset();
    });
});