import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import TimestampComponent from './TimestampComponent.jsx';
import ErrorViewComponent from './ErrorViewComponent.jsx';

class StatusComponent extends React.Component {
    static propTypes = {
        status: PropTypes.string.isRequired,
        projectId: PropTypes.string.isRequired
    };

    constructor(props){
        super(props);

        this.state = {
            loading: false,
            expanded: false,
            error: null,
            statusHistory: []
        };

        this.openExpander = this.openExpander.bind(this);
    }

    componentDidUpdate(newProps, newState){
        if(newProps.projectId!==this.props.projectId) this.setState({statusHistory: []});
    }

    loadStatusHistory(){
        this.setState({loading: true},()=>{
            axios.get("/gnmplutostats/project/"+this.props.projectId+"/status_history").then(response=>{
                this.setState({statusHistory: response.data, loading: false},()=>console.log("set state", this.state))
            }).catch(error=>{
                console.error(error);
                this.setState({error: error, loading: false});
            })
        })
    }

    openExpander(){
        this.setState({expanded: true},()=>{
            if(this.state.statusHistory.length===0) this.loadStatusHistory();
        });
    }

    expander(){
        return this.state.expanded ?
            <a className="expander-link control-link" onClick={()=>this.setState({expanded:false})}>hide history</a> :
            <a className="expander-link control-link" onClick={this.openExpander}>show history</a>
    }

    render(){
        return <div>
            <span className="project-current-status">{this.props.status}</span>
            {this.expander()}
            <ul className="project-history-list" style={{display: this.state.expanded ? "block" : "none"}}>
                {
                    this.state.statusHistory.map(entry=><li key={entry.uuid} className="project-history-list-entry">
                        <TimestampComponent timestamp={entry.timestamp} format="ddd Do MMM YYYY, HH:mm" relative={false}/>
                        <span className="user-holder"><i className="fa fa-user inline-icon"/>{entry.user}</span>
                        <span className="project-new-status">{entry.newvalue}</span>
                    </li>)
                }
            </ul>
            <ErrorViewComponent error={this.state.error}/>
        </div>
    }
}

export default StatusComponent;