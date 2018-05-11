import React from 'react';
import PropTypes from 'prop-types';
import TimestampComponent from './TimestampComponent.jsx';
import ErrorViewComponent from './ErrorViewComponent.jsx';
import DurationComponent from './DurationComponent.jsx';
import StatusComponent from './StatusComponent.jsx';
import ProjectStorageChart from './ProjectStorageChart.jsx';

import axios from 'axios';

class ProjectSummaryArea extends React.Component {
    static propTypes = {
        projectId: PropTypes.string.isRequired
    };

    constructor(props){
        super(props);

        this.state = {
            loading: false,
            refreshing: false,
            error: null,
            projectInfo: {}
        };

        this.refreshProject = this.refreshProject.bind(this);
    }

    componentDidUpdate(oldProps,oldState){
        if(oldProps.projectId!==this.props.projectId) {
            this.setState({timerId: null, refreshing: false}, ()=>this.reloadData());
        }
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

    getCookie(name){
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        if (match) return match[2]; //array contents - matched string, first group, second group
    }

    refreshProject(){
        this.setState({refreshing: true}, ()=>{
            axios.put("/gnmplutostats/project/" + this.props.projectId + "/update", {},{
                headers: {'X-CSRFToken': this.getCookie('csrftoken')}
            }).then(response=>{
                this.setState({
                    refreshing: false,
                    error:null,
                    timerId: window.setTimeout(()=>{this.reloadData()},10000)
                }, ()=>this.reloadData())
            }).catch(error=> {
                console.error(error);
                this.setState({refreshing: false, error:error})
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
                    <td className="project-summary-header">Title</td>
                    <td>{this.state.projectInfo.project_title} <a href={"/project/" + this.props.projectId} target="_blank" style={{marginLeft: "2em"}}>Open project >>></a>
                        <button style={{float: "right"}}
                                disabled={this.state.refreshing}
                                onClick={this.refreshProject}
                                className={this.state.refreshing ? "blue-button" : "blue-button disabled"}
                        >Refresh</button>
                    </td>
                </tr>
                <tr>
                    <td className="project-summary-header">Status</td>
                    <td><StatusComponent status={this.state.projectInfo.project_status} projectId={this.props.projectId}/></td>
                </tr>
                <tr>
                    <td className="project-summary-header">Last scanned</td>
                    <td><TimestampComponent timestamp={this.state.projectInfo.last_scan} relative={true}/></td>
                </tr>
                <tr>
                    <td className="project-summary-header">Scan took</td>
                    <td><DurationComponent durationSeconds={this.state.projectInfo.last_scan_duration}/></td>
                </tr>
                <tr>
                    <td className="project-summary-header">Scan error?</td>
                    <td><pre>{this.state.projectInfo.last_scan_error}</pre></td>
                </tr>
                <tr>
                    <td><a href={"/gnm_archiver/troubleshooter?project_id="+this.props.projectId} target="_blank">Open archive troubleshooter</a></td>
                </tr>
                </tbody>
            </table>
        }
    }

    render(){
        return <div className="project-summary-area" style={{display: this.props.projectId ? "block" : "none"}}>
            <span className="project-summary-header">Project {this.props.projectId}</span>
            {this.mainContent()}
            <div style={{height: "260px"}}><ProjectStorageChart projectId={this.props.projectId}/></div>
        </div>
    }
}

export default ProjectSummaryArea;