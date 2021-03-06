import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import {Bar, Doughnut, Pie} from 'react-chartjs-2';
import {Chart} from 'chart.js';

/*
thanks to https://stackoverflow.com/questions/13851088/how-to-bind-function-arguments-without-binding-this
this allows us to bind the value of `this` in the context of the React object to an arbitary argument
in the context of the callback without over-writing the callback's `this` context (in this case, the chart)
 */
Function.prototype.bindArgs =
    function (...boundArgs)
    {
        let context = this;
        return function(...args) { return context.call(this, ...boundArgs, ...args); };
    };

class StorageUsageCharts extends React.Component {
    static propTypes = {
        onProjectSelected: PropTypes.func.isRequired
    };

    constructor(props){
        super(props);

        this.state = {
            known_storages: [],
            visible_storages: [],
            error: null,
            datasets: [],
            showAbsolute: false,
            showLegend: false,
            zoomed: false,
            projectLimit: 30,
            maximumStorageValue: 0
        }
    }

    backgroundColourFor(idx,total,hover,name){
        if(name==="Uncounted") return "rgb(200,200,200)";
        if(name==="Other") return "rgb(100,100,100)";

        const hue = (360.0/total)*idx;
        const sat = hover ? "20%": "50%";
        const light = "50%";
        return "hsl("+hue+","+sat+","+light+")";
    }

    componentWillMount() {
        this.updateGraph();
    }

    componentDidUpdate(oldProps,oldState){
        if(oldState.showAbsolute!==this.state.showAbsolute) this.updateGraph();
    }

    updateGraph(){
        const args = this.state.showAbsolute ? "&absolute=true" : "";
        const total_entry_count=this.state.projectLimit;

        const futures = [
            axios.get('/gnmplutostats/projectsize/project/graph?limit='+total_entry_count+args),
            axios.get('/gnmplutostats/projectsize/storage/totals')
        ];

        Promise.all(futures).then(responses=>{
            if(responses[0].data.hasOwnProperty("status") && responses[0].data.status==="error"){
                console.error(responses[0].data.detail);
                return;
            }
            this.setState({
                known_storages: responses[0].data.storage_key,
                visible_storages: responses[0].data.storage_key,
                datasets: responses[0].data.projects.map((proj,idx)=>{
                    return {
                        label: proj.project_id,
                        backgroundColor: this.backgroundColourFor(idx, total_entry_count, false, proj.project_id),
                        borderColor: 'rgba(255,99,132,1)',
                        borderWidth: 0,
                        hoverBackgroundColor: this.backgroundColourFor(idx, total_entry_count, proj.project_id),
                        hoverBorderColor: 'rgba(255,99,132,1)',
                        data: proj.sizes
                    }
                }),
                maximumStorageValue: Object.keys(responses[1].data)
                    .map(storageName=>responses[1].data[storageName])
                    .reduce((acc,entry)=>entry.total>acc ? entry.total : acc, 0)
            })
        }).catch(err=>{
            console.error(err);
            this.setState({error: err})
        })
    }

    /**
     * returns the total amount of storage that has been broken down for us.
     */
    total_labelled_absolute(){
        return this.state.datasets
            .filter(entry=>entry.label!=="Uncounted" && entry.label!=="Other")
            .reduce((acc,entry)=>acc+Math.max(...entry.data), 0)
    }

    total_labelled_relative(){
        return this.total_labelled_absolute()/this.state.maximumStorageValue;
    }

    zoomControl(){
        return this.state.zoomed ? <a className="control-link" onClick={()=>this.setState({zoomed: false})}>zoom out</a> : <a className="control-link" onClick={()=>this.setState({zoomed: true})}>zoom in</a>
    }

    render(){
        const chartData = {
            labels: this.state.known_storages,
            datasets: this.state.datasets
        };

        const tickConfig = this.state.showAbsolute ? {
            callback: (value, index, values)=>(value/1024).toString() + "Tb",
            max: this.state.zoomed ? this.total_labelled_absolute() : this.state.maximumStorageValue
        } : {
            callback: (value, index, values)=>(value *100).toString() + "%",
            max: this.state.zoomed ? this.total_labelled_absolute() : 1.0
        };

        return <div>
            <h3>Storage Capacity</h3>
            <span className="chart-controls">
                <input id="id-show-absolute" type="checkbox" value={this.state.showAbsolute} onChange={evt=>this.setState({showAbsolute: !this.state.showAbsolute})}/>
                <label style={{paddingRight: "1em"}} htmlFor="id-show-absolute">Absolute Values</label>
                <input id="id-show-legend" type="checkbox"
                       style={{paddingLeft: "1em"}}
                       value={this.state.showLegend}
                       onChange={evt=>this.setState({showLegend: !this.state.showLegend})}/>
                <label style={{paddingRight: "1em"}} htmlFor="id-show-legend">Show Legend</label>
                <input id="id-project-limit" style={{ width: "40px"}} type="number" value={this.state.projectLimit} onChange={evt=>this.setState({projectLimit: parseInt(evt.target.value)})}/>
                <label style={{paddingRight: "1em"}} htmlFor="id-project-limit">Limit projects</label>
                {this.zoomControl()}
            </span>
        <div className="chart-holder" style={{height: "700px"}}>
            <Bar data={chartData}
                 options={{
                     scales: {
                         xAxes: [{
                             stacked: true,
                             gridLines: {
                                 display: false
                             }
                         }],
                         yAxes: [{
                             display: true,
                             stacked:true,
                             gridLines: {
                                 display: false
                             },
                             ticks: tickConfig
                         }]
                     },
                     maintainAspectRatio: false,
                     legend: {
                         display: this.state.showLegend,
                         position: "right"
                     },
                     tooltips: {
                         mode: "label",
                         callbacks: {
                             label: (ttitem, data)=>{
                                 let label = data.datasets[ttitem.datasetIndex].label || '';

                                 if (label) {
                                     label += ': ';
                                 }
                                 label += Math.round(ttitem.yLabel * 100) / 100;
                                 return label;
                             }
                         },
                         enabled: false
                     },
                     barPercentage: 1.0,
                     categoryPercentage: 1.0,
                     onClick: this.chartClicked.bindArgs(this)
                 }}/>
        </div>
        </div>
    }

    chartClicked(reactobj,event, activeElems){
        const elemData = this.getElementAtEvent(event)[0];

        const clickedName = (elemData["_view"]["datasetLabel"]);
        const clickedStorage = (elemData["_view"]['label']);
        console.log("You clicked " + clickedName);
        reactobj.props.onProjectSelected(clickedName, clickedStorage);
    }
}

export default StorageUsageCharts;