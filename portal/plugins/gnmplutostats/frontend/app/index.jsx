import React from 'react';
import {render} from 'react-dom';
import StorageUsageCharts from './StorageUsageCharts.jsx';
import ProjectSummaryArea from './ProjectSummaryArea.jsx';
import ScanHealthGraph from './ScanHealthGraph.jsx';

class App extends React.Component {
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
                    <StorageUsageCharts onProjectSelected={(newProject,newStorage)=>this.setState({selectedProject: newProject, selectedStorage:newStorage})}/>
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

render(<App/>, document.getElementById('app'));