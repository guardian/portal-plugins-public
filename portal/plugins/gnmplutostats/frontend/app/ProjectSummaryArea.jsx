import React from 'react';
import PropTypes from 'prop-types';
import TimestampComponent from './TimestampComponent.jsx';
import ErrorViewComponent from './ErrorViewComponent.jsx';
import DurationComponent from './DurationComponent.jsx';
import StatusComponent from './StatusComponent.jsx';

import axios from 'axios';

class ProjectSummaryArea extends React.Component {
    static propTypes = {
        projectId: PropTypes.string.isRequired
    };

    constructor(props){
        super(props);

        this.state = {
            loading: false,
            error: null,
            projectInfo: {}
        }
    }

    componentDidUpdate(oldProps,oldState){
        if(oldProps.projectId!==this.props.projectId) this.reloadData();
    }

    reloadData(){
        this.setState({loading:true}, ()=>{
            axios.get("/gnmplutostats/project/" + this.props.projectId + "/info").then(response=>{
                this.setState({loading: false, projectInfo: response.data, error: null})
            }).catch(err=>{
                this.setState({loading: false, error: err});
            })
        })
    }

    mainContent(){
        if(this.state.loading){
            return <span>loading...</span>
        } else if(this.state.error) {
            return <ErrorViewComponent error={this.state.error}/>
        } else if(!this.state.projectInfo || this.state.projectInfo==={}){
            return <span/>
        } else {
            return <table className="project-summary-content">
                <tbody>
                <tr>
                    <td>Title</td>
                    <td>{this.state.projectInfo.project_title}</td>
                </tr>
                <tr>
                    <td>Status</td>
                    <td><StatusComponent status={this.state.projectInfo.project_status} projectId={this.props.projectId}/></td>
                </tr>
                <tr>
                    <td>Last scanned at</td>
                    <td><TimestampComponent timestamp={this.state.projectInfo.last_scan} relative={true}/></td>
                </tr>
                <tr>
                    <td>Scan took</td>
                    <td><DurationComponent durationSeconds={this.state.projectInfo.last_scan_duration}/></td>
                </tr>
                <tr>
                    <td>Scan error?</td>
                    <td><pre>{this.state.projectInfo.last_scan_error}</pre></td>
                </tr>
                </tbody>
            </table>
        }
    }

    render(){
        return <div className="project-summary-area" style={{display: this.props.projectId ? "block" : "none"}}>
            <span className="project-summary-header">Project {this.props.projectId}</span>
            {this.mainContent()}
        </div>
    }
}

export default ProjectSummaryArea;