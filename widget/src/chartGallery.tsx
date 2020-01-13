import React, { Component } from 'react';
// import ReactDOM from 'react-dom';
// import ToolComponent from './tool';
import { VegaLite } from 'react-vega';
// import { VisualizationSpec } from 'vega-embed';
interface chartGalleryProps{
    graphSpec: object[]
}
class ChartGalleryComponent extends Component<chartGalleryProps,any> {
    constructor(props:any) {
        super(props);
    }
    render() {
        console.log("this.props.graphSpec:",this.props.graphSpec)
        const galleryItems = this.props.graphSpec.map((item,idx) =>
                <div key={idx.toString()}
                     className="graph-container"
                     id={"graph-container-".concat(idx.toString())}>
                    <VegaLite spec={item}  
                              padding={{left: 10, top: 5, right: 5, bottom: 5}} />
                    {/* <ToolComponent graphIdx={idx}/> */}
                </div>  
            );
        return (
            <div id="staticOuterDiv" className="recommendationStaticContentOuter">
                <div id="mult-graph-container" className= "recommendationContentInner">
                    {galleryItems}
                </div>
            </div>
        );
    }
}
export default ChartGalleryComponent;