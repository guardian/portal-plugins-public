import React from 'react';
import StorageUsageCharts from './StorageUsageCharts.jsx';
import PropTypes from 'prop-types';

class ByCategoryChart extends StorageUsageCharts {
    static propTypes = {
        onProjectSelected: PropTypes.func.isRequired
    };

    constructor(props){
        super(props);
        this.data_url = '/gnmplutostats/projectsize/category/graph';
    }
}

export default ByCategoryChart;