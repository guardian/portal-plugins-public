import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import {HorizontalBar} from 'react-chartjs-2';

class ProjectStorageChart extends React.Component {
    static propTypes = {
        projectId: PropTypes.string.isRequired
    };

    constructor(props){
        super(props);

        this.state = {
            loading: false,
            error: null,
            data: []
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

    loadData(){
        this.setState({loading: true}, ()=>
            axios.get("/gnmplutostats/project/" + this.props.projectId + "/usage").then(response=>{
                this.setState({loading: false, data: response.data})
            }).catch(error=>{
                console.error(error);
                this.setState({loading: false, error: error});
            })
        );
    }

    componentDidUpdate(oldProps,oldState){
        if(oldProps.projectId!==this.props.projectId) this.loadData();
    }

    componentWillMount(){
        this.loadData();
    }

    render(){
        const total_entry_count = this.state.data.length;

        return <HorizontalBar
            data={{
                labels: this.state.data.map(entry=>entry.storage_id),
                datasets:[{
                        label: "Storage used",
                        backgroundColor: this.backgroundColourFor(2, total_entry_count, false),
                        borderWidth: 0,
                        hoverBackgroundColor: this.backgroundColourFor(2, total_entry_count, true),
                        hoverBorderColor: 'rgba(255,99,132,1)',
                        data: this.state.data.map(entry=>entry.size_used_gb)
                }]
            }}
            options={{
                scales: {
                    xAxes: [{
                        stacked: false,
                        gridLines: {
                            display: true
                        },
                        ticks: {
                            callback: (value, index, values)=>value.toString() + "Gb"
                        }
                    }],
                    yAxes: [{
                        display: true,
                        stacked:false,
                        gridLines: {
                            display: false
                        }
                    }]
                },
                maintainAspectRatio: false,
                tooltips: {
                    mode: "label"
                },
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }}
        />
    }
}

export default ProjectStorageChart;