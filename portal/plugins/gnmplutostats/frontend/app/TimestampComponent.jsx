import React from 'react';
import PropTypes from 'prop-types';

class TimestampComponent extends React.Component {
    static propTypes = {
        timestamp: PropTypes.string.isRequired,
        format: PropTypes.string,
        relative: PropTypes.bool.isRequired
    };

    constructor(props){
        super(props);

        this.defaultFormat = "ddd Do MMM, HH:mm";
        this.state = {

        }
    }

    render(){
        const formatString = this.props.format ? this.props.format : this.defaultFormat;

        if(this.props.relative){
            return <span className="timestamp-relative">{moment(this.props.timestamp).fromNow()}; {moment(this.props.timestamp).format(formatString)}</span>
        } else {
            return <span className="timestamp-absolute">{moment(this.props.timestamp).format(formatString)}</span>
        }
    }
}

export default TimestampComponent;