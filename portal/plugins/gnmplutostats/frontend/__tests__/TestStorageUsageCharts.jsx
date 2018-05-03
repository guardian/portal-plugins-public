import React from 'react';
import moxios from 'moxios';
import sinon from 'sinon';
import {shallow} from 'enzyme';
import StorageUsageCharts from '../app/StorageUsageCharts.jsx';

describe("StorageUsageCharts", ()=>{
    beforeEach(()=>moxios.install());
    afterEach(()=>moxios.uninstall());

    it("updateGraph() should load in data and present it to the component state", (done)=>{
        const projectSelectedCb = sinon.spy();

        const rendered = shallow(<StorageUsageCharts onProjectSelected={projectSelectedCb}/>);

        return moxios.wait(()=>{
            const graphRequest = moxios.requests.at(0);
            const storageRequest = moxios.requests.at(1);

            try {
                expect(graphRequest.url).toEqual("/gnmplutostats/projectsize/project/graph?limit=10");
                expect(storageRequest.url).toEqual("/gnmplutostats/projectsize/storage/totals");
            } catch(err){
                done.fail(err);
            }

            graphRequest.respondWith({
                status: 200,
                response: {"status": "ok", "storage_key": ["KP-11", "KP-16", "KP-2", "KP-21", "KP-3", "KP-4", "KP-5", "KP-6", "KP-7", "KP-71", "KP-8", "KP-9"], "projects": [{"project_id": "KP-21048", "sizes": [0.0, 0.00016739203213927018, 0.00592484887342004, 0.0, 0.007467287404138122, 0.0, 0.0, 0.0, 0.0, 0.0, 0.00023023630617242607, 0.0]}, {"project_id": "KP-22875", "sizes": [0.0, 0.00017785403414797456, 0.006062236673383403, 0.0, 0.004229158144010325, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0005441949054984616, 0.0]}, {"project_id": "KP-19979", "sizes": [0.0, 0.0, 0.004339164682176223, 0.0, 0.0048802410735378, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0003872156058354438, 0.0]}, {"project_id": "KP-25655", "sizes": [0.0, 0.0, 0.0025473987909873604, 0.0, 0.0031632259142529546, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}, {"project_id": "KP-23677", "sizes": [0.0, 0.0, 0.0018375618245099834, 0.0, 0.0014865433258237928, 0.0, 0.0, 8.369601606963509e-05, 8.369601606963509e-05, 0.0, 9.418757979781066e-05, 0.0]}, {"project_id": "KP-26441", "sizes": [0.0, 0.0, 0.0013738779996336325, 0.0, 0.001630588221736951, 0.0, 0.0, 0.0, 0.0, 0.0, 2.093057328840237e-05, 0.0]}, {"project_id": "KP-27363", "sizes": [0.0, 0.0, 0.001310908591317091, 0.0, 0.001544161284189056, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0465286644201185e-05, 0.0]}, {"project_id": "KP-26993", "sizes": [0.0, 0.0, 0.000715561458142517, 0.0, 0.0012560714923627397, 0.0, 0.0, 5.231001004352193e-05, 0.0, 0.0, 0.0013709525503903552, 0.0]}, {"project_id": "KP-25666", "sizes": [0.0, 0.0, 0.001099102399706906, 0.0, 0.0012215007173435816, 0.0, 0.0, 0.0, 0.0, 0.0, 7.32570065094083e-05, 0.0]}, {"project_id": "KP-24201", "sizes": [0.0, 0.0, 0.0010876534163766257, 0.0, 0.0011984535339974764, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}, {"project_id": "Other", "sizes": [0.0, 0.000680026518600746, 0.042155006077608595, 0.0, 0.04420433588255667, 0.0, 5.231001004352193e-05, 0.0038814013223340085, 8.369514044174685e-05, 6.277201205222631e-05, 0.014839747876176673, 0.0]}, {"project_id": "Uncounted", "sizes": [1.0, 0.9993199698694342, 0.9578448433779081, 1.0, 0.95579550234217, 1.0, 0.9999476899899564, 0.9961185972547707, 0.9999163039839304, 0.9999372279879478, 0.9851602235385227, 1.0]}]}
            }).then(()=>{

            }).catch(error=>{
                console.error(error);
                done.fail(error);
            });

            storageRequest.respondWith({
                status: 200,
                response:{
                    "KP-21": {
                        "total": 100500,
                        "counted": 0
                    },
                    "KP-8": {
                        "total": 100500,
                        "counted": 1418
                    },
                    "KP-9": {
                        "total": 16750,
                        "counted": 0
                    },
                    "KP-6": {
                        "total": 100500,
                        "counted": 371
                    },
                    "KP-7": {
                        "total": 100500,
                        "counted": 8
                    },
                    "KP-4": {
                        "total": 100500,
                        "counted": 0
                    },
                    "KP-5": {
                        "total": 100500,
                        "counted": 5
                    },
                    "KP-2": {
                        "total": 179923,
                        "counted": 7364
                    },
                    "KP-3": {
                        "total": 177391,
                        "counted": 7672
                    },
                    "KP-16": {
                        "total": 100500,
                        "counted": 65
                    },
                    "KP-71": {
                        "total": 100500,
                        "counted": 6
                    },
                    "KP-11": {
                        "total": 16750,
                        "counted": 0
                    }
                }
            }).then(()=>{
                expect(rendered.instance().state.error).toEqual(null);
                expect(rendered.instance().state.maximumStorageValue).toEqual(179923);
                expect(rendered.instance().state.datasets.length).toEqual(12);
                done();
            }).catch((err)=>done.fail(err));
        })
    })
});