import React from 'react';

class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            selectedProject: null
        }
    }

    render(){
        return <div id="app">
            <div className="graph-area">
                <StorageUsageCharts onProjectSelected={newProject=>this.setState({selectedProject: newProject})}/>
                <ProjectSummaryArea projectId={this.state.selectedProject}/>
            </div>
        </div>
    }
}

render(<App/>, document.getElementById('app'));