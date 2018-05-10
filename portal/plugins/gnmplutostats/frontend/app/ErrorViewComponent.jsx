import React from 'react';
import PropTypes from 'prop-types';

class ErrorViewComponent extends React.Component {
    static propTypes = {
        error: PropTypes.object.isRequired
    };

    /* expects axios error response in props.error */
    constructor(props){
        super(props);
    }

    niceMakeString(someObject){
        if(someObject.isObjectLike({})){
            return this.dictToList(someObject);
        } else if(Array.isArray(someObject)){
            return someObject.reduce((acc, item)=> acc+this.niceMakeString(item), "");
        } else {
            return someObject.toString();
        }

    }
    dictToList(dictObject){
        return <ul>
            {Object.keys(dictObject).map(key=>
                <li>{key}: {this.niceMakeString(dictObject[key])}</li>
            )}
        </ul>
    }

    bestErrorString(errorObj){
        if(errorObj.hasOwnProperty("detail")) return JSON.stringify(errorObj.detail);
        return errorObj.toString();
    }

    render(){
        if(!this.props.error){
            return <p className="error-text"/>
        }

        if (this.props.error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            return <p className="error-text">Server error {this.props.error.response.status}: {this.bestErrorString(this.props.error.response.data)}</p>
        } else if (this.props.error.request) {
            // The request was made but no response was received
            // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
            // http.ClientRequest in node.js
            console.error("Failed request: ", this.props.error.request);
            return <p className="error-text">No response from server. See console log for more details.</p>
        } else {
            // Something happened in setting up the request that triggered an Error
            console.error('Axios error setting up request: ', this.props.error.message);
            return <p className="error-text">Unable to set up request. See console log for more details.</p>
        }

    }
}

export default ErrorViewComponent;