import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import {Bar, Doughnut, Pie} from 'react-chartjs-2';

class StorageUsageBar extends React.Component {
    static propTypes = {
        storageId: PropTypes.string.isRequired,
        visible: PropTypes.bool.isRequired,
        totalAccountedFor: PropTypes.number.isRequired,
        projectCountLimit: PropTypes.number
    };

    constructor(props){
        super(props);

        this.state = {
            visible: true,
            chartData: null
        }
    }

    backgroundColourFor(idx,total){
        const hue = (360.0/total)*idx;
        const sat = "50%";
        const light = "50%";
        return "hsl("+hue+","+sat+","+light+")";
    }

    componentWillMount(){
        const limit = this.props.projectCountLimit ? this.props.projectCountLimit : 20;

        axios.get('/gnmplutostats/projectsize/storage/' + this.props.storageId + "?limit=" + limit).then(response=>{
            const total_entry_count = response.data.length;
            this.setState({chartData:{
                labels: [this.props.storageId],
                datasets: response.data.map((entry,idx)=>{
                    return {
                        label: entry.project_id,
                        backgroundColor: this.backgroundColourFor(idx,total_entry_count),
                        borderColor: 'rgba(255,99,132,1)',
                        borderWidth: 1,
                        hoverBackgroundColor: 'rgba(255,99,132,0.4)',
                        hoverBorderColor: 'rgba(255,99,132,1)',
                        data: [entry.size_used_gb]
                    }
                })
            }})
        }).catch(error=>{
            console.error(error);
            this.setState({error: error});
        })
    }

    render(){
        if(!this.state.chartData) return <div/>;
        console.log(this.state.chartData);
        return <div id="storage-bar-holder" style={{width: "100%", height: "100%", display: "inline-block"}}>
            <Bar data={this.state.chartData}
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
                     barThickness: 26,
                     maintainAspectRatio: false,
                     gridLines: false
                 }}/>
        </div>
    }
}

export default StorageUsageBar;