import React, { Component } from 'react';
import { VegaLite } from 'react-vega';
import _ from 'lodash';
interface currentViewProps{
    currentViewSpec: object
}
class CurrentViewComponent extends Component<currentViewProps,any> {
    constructor(props:any) {
        super(props);
    }
    render() {
        console.log("this.props.currentViewSpec:",this.props.currentViewSpec)
        let selectedVis = function (vizLabel:string){
            // console.log("selectedVis event:",event)
            console.log(vizLabel)
        }
        if (!_.isEmpty(this.props.currentViewSpec)){
            return (
                <div id="mainVizContainer">
                    <h2 id="mainVizTitle">Current View</h2>
                    <div id="mainVizInnerContainer">
                        <div className="vizContainer" onClick={()=>selectedVis("main")}>
                            <VegaLite spec={this.props.currentViewSpec}
                                      padding={{left: 10, top: 5, right: 5, bottom: 5}} 
                                      actions={false}/>
                        </div>
                    </div>
                </div>
            );
        }else{
            return (
                <div className="placeHolderVizContainer">
                </div>
            )
        }
        
    }
}
export default CurrentViewComponent;