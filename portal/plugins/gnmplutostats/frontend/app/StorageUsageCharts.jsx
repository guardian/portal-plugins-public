import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import StorageUsageBar from './StorageUsageBar.jsx';
import {Bar, Doughnut, Pie} from 'react-chartjs-2';

/**
 * How it _SHOULD_ work
 *
 * each project is a dataset
 * this contains an array of entries of capacity used in each storage
 * so i am loading the data the wrong way around
 *
 * need to get a list of all projects
 * then query each one
 *
 */
class StorageUsageCharts extends React.Component {
    constructor(props){
        super(props);

        this.state = {
            known_storages: [],
            visible_storages: [],
            error: null,
            datasets: []
        }
    }

    backgroundColourFor(idx,total,hover){
        const hue = (360.0/total)*idx;
        const sat = hover ? "20%": "50%";
        const light = "50%";
        return "hsl("+hue+","+sat+","+light+")";
    }

    dataSetForResult(result,idx){
        const total_entry_count = result.data.length;
        return {
            label: result.data.map(entry=>entry.project_id),
            stack: result.data[0].storage_id,
            backgroundColor: this.backgroundColourFor(idx, total_entry_count, false),
            borderColor: 'rgba(255,99,132,1)',
            borderWidth: 1,
            hoverBackgroundColor: this.backgroundColourFor(idx, total_entry_count, true),
            hoverBorderColor: 'rgba(255,99,132,1)',
            data: result.data.map((entry, idx) => entry.size_used_gb)
        }
    }

    updateDatasets(){
        const futuresList = this.state.known_storages.map(entry=>axios.get("/gnmplutostats/projectsize/storage/" + entry.storageId));

        Promise.all(futuresList).then(storageResults=>{
            const multidimensional = storageResults.map((result, idx)=>this.dataSetForResult(result,idx));
            console.log(multidimensional);
            this.setState({
                datasets: [].concat(...multidimensional)
            });

            }).catch(err=>{
                console.log(err);
                this.setState({error: err});
            })
    }

    componentWillMount(){
        const total_entry_count=10;
        axios.get('/gnmplutostats/projectsize/project/graph?limit='+total_entry_count).then(response=>{
            this.setState({
                known_storages: response.data.storage_key,
                visible_storages: response.data.storage_key,
                datasets: response.data.projects.map((proj,idx)=>{
                    return {
                        label: proj.project_id,
                        backgroundColor: this.backgroundColourFor(idx, total_entry_count, false),
                        borderColor: 'rgba(255,99,132,1)',
                        borderWidth: 1,
                        hoverBackgroundColor: this.backgroundColourFor(idx, total_entry_count, true),
                        hoverBorderColor: 'rgba(255,99,132,1)',
                        data: proj.sizes
                    }
                })
            })
        }).catch(err=>{
            console.error(err);
            this.setState({error: err})
        })
    }

    render(){
        const chartData = {
            labels: this.state.known_storages,
            datasets: this.state.datasets
        };
        console.log(chartData);

        return <div className="chart-holder">
            <Bar data={chartData}
                 options={{
                     scales: {
                         xAxes: [{
                             stacked:true,
                             gridLines: {
                                 display: false
                             }
                         }],
                         yAxes: [{
                             stacked:true,
                             gridLines: {
                                 display: false
                             }
                         }]
                     },
                     maintainAspectRatio: false,
                     legend: {
                         display: false
                     }
                 }}/>
        </div>

    }
}

export default StorageUsageCharts;