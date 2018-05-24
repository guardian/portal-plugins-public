import React from 'react';
import ByCategoryChart from './ByCategoryChart.jsx';
import ProjectSummaryArea from './ProjectSummaryArea.jsx';
import ScanHealthGraph from './ScanHealthGraph.jsx';

class ViewByCategory extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            selectedProject: null,
            selectedStorage: null
        }
    }

    render(){
        return <div style={{width: "100%", height: "100%",overflow:"hidden"}}>
            <div id="left-column" className="left-column">
                <ByCategoryChart onProjectSelected={(newProject,newStorage)=>this.setState({selectedProject: newProject, selectedStorage:newStorage})}/>
            </div>
            <div id="right-column" className="right-column">
                <ProjectSummaryArea projectId={this.state.selectedProject}/>
            </div>
            <div id="bottom-panel" className="full-width-bottom">
                <ScanHealthGraph/>
            </div>
        </div>
    }
}

export default ViewByCategory;
