import React from 'react';
import axios from 'axios';
import {HorizontalBar} from 'react-chartjs-2';
import PropTypes from 'prop-types'

class ScanHealthGraph extends React.Component {
    constructor(props){
        super(props);

        this.state = {
            chartData: {},
            error: null,
            loading:false
        }
    }

    componentWillMount(){
        this.refreshData();
    }

    refreshData(){
        this.setState({loading: true}, ()=>
            axios.get("/gnmplutostats/projectsize/receipt/stats").then(response=>{
                this.setState({chartData: response.data, loading: false})
            }).catch(error=>{
                console.log(error);
                this.setState({error: error, loading: false})
            })
        );
    }

    backgroundColourFor(idx,total,hover){
        const hue = (360.0/total)*idx;
        const sat = hover ? "20%": "50%";
        const light = "50%";
        return "hsl("+hue+","+sat+","+light+")";
    }

    /**
     * convert the chart data provided by the endpoint to the form that the chartjs widget wants
     */
    renderChartData(){
        const total_entry_count = Object.keys(this.state.chartData).length;
        return {
            labels: [""],
            datasets: Object.keys(this.state.chartData).map((keyname,idx)=>{
                return {
                    label: keyname,
                    backgroundColor: this.backgroundColourFor(idx, total_entry_count, false),
                    borderColor: 'rgba(255,99,132,1)',
                    borderWidth: 0,
                    hoverBackgroundColor: this.backgroundColourFor(idx, total_entry_count, true),
                    hoverBorderColor: 'rgba(255,99,132,1)',
                    data: [this.state.chartData[keyname]]
                }
            })
        }
    }

    render(){
        if(this.state.loading) return <div>loading</div>;
        return <div className="chart-holder">
            <h3>Scanner Status</h3>
            <HorizontalBar data={this.renderChartData()}
                 options={{
                     scales: {
                         xAxes: [{
                             position: top,
                             stacked: true,
                             gridLines: {
                                 display: false
                             }
                         }],
                         yAxes: [{
                             display: false,
                             stacked:true,
                             gridLines: {
                                 display: false
                             }
                         }]
                     },
                     maintainAspectRatio: false,
                     legend: {
                         display: true,
                         position: "right"
                     },
                     tooltips: {
                         mode: "label"
                     }
                 }}/>
        </div>
    }
}

export default ScanHealthGraph;
