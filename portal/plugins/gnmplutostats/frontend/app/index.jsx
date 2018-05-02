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
        return <div>
                <StorageUsageCharts onProjectSelected={newProject=>this.setState({selectedProject: newProject})}/>
                <ProjectSummaryArea projectId={this.state.selectedProject}/>
        </div>
    }
}

render(<App/>, document.getElementById('app'));