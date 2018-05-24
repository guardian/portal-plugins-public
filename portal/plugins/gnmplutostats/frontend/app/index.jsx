import React from 'react';
import {render} from 'react-dom';
import {
    BrowserRouter as Router,
    Route,
    Link,
    Switch
} from 'react-router-dom';
import ViewByProject from './ViewByProject.jsx';
import ViewByCategory from './ViewByCategory.jsx';

class App extends React.Component {
    render(){
        return <Switch>
            <Route path="/by-project" component={ViewByProject}/>
            <Route path="/by-category" component={ViewByCategory}/>
        </Switch>
    }
}


render(<Router basename="/gnmplutostats/storagedash"><App/></Router>, document.getElementById('app'));