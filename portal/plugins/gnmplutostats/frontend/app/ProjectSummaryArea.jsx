import React from 'react';
import PropTypes from 'prop-types';
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
            return <span>Something went wrong, consult the browser console</span>
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
                    <td>{this.state.projectInfo.project_status}</td>
                </tr>
                <tr>
                    <td>Last scanned at</td>
                    <td>{this.state.projectInfo.last_scan}</td>
                </tr>
                <tr>
                    <td>Scan took</td>
                    <td>{this.state.projectInfo.last_scan_duration}</td>
                </tr>
                <tr>
                    <td>Scan error?</td>
                    <td>{this.state.projectInfo.last_scan_error}</td>
                </tr>
                </tbody>
            </table>
        }
    }

    render(){
        return <div className="project-summary-area">
            <span className="project-summary-header">Project {this.props.projectId}</span>
            {this.mainContent()}
        </div>
    }
}

export default ProjectSummaryArea;