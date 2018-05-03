import React from 'react';
import {render} from 'react-dom';
import StorageUsageCharts from './StorageUsageCharts.jsx';
import ProjectSummaryArea from './ProjectSummaryArea.jsx';

class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            selectedProject: null
        }
    }

    render(){
        return <div style={{width: "100%", height: "100%",overflow:"hidden"}}>
                <StorageUsageCharts onProjectSelected={newProject=>this.setState({selectedProject: newProject})}/>
                <ProjectSummaryArea projectId={this.state.selectedProject}/>
        </div>
    }
}

render(<App/>, document.getElementById('app'));