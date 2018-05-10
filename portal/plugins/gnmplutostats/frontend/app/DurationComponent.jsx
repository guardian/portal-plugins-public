import React from 'react';
import PropTypes from 'prop-types';

class DurationComponent extends React.Component {
    static propTypes = {
        durationSeconds: PropTypes.number.isRequired
    };

    render(){
        if(this.props.durationSeconds<60){
            return <span className="duration">{this.props.durationSeconds} seconds</span>
        }

        const hours = Math.floor(this.props.durationSeconds/3600);
        const mins = Math.floor((this.props.durationSeconds - (hours *3600))/60);
        const seconds = this.props.durationSeconds - (mins*60) - (hours *3600);

        if(hours>0){
            return <span className="duration">{hours} hours, {mins} minutes, {seconds} seconds</span>
        } else {
            return <span className="duration">{mins} minutes, {seconds} seconds</span>
        }
    }
}

export default DurationComponent;