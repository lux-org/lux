import React, { Component } from 'react';
// import ReactDOM from 'react-dom';
// import ToolComponent from './tool';
import SelectableCard from './selectableCard';
import { VegaLite } from 'react-vega';
// import { VisualizationSpec } from 'vega-embed';
interface chartGalleryProps{
    multiple: boolean,
    maxSelectable: number,
    onChange: Function,
    graphSpec: object[]
}

class ChartGalleryComponent extends Component<chartGalleryProps,any> {
    constructor(props:any) {
        super(props);
        var selected = props.multiple ? [] : -1;
        var initialState = {
        selected: selected
        };
        this.state = initialState;
    }
    onItemSelected(index) {
        // Implementation based on https://codepen.io/j-burgos/pen/VpQxLv
        this.setState((prevState, props) => {
          if (props.multiple) {
            var selectedIndexes = prevState.selected;
            var selectedIndex = selectedIndexes.indexOf(index);
            if (selectedIndex > -1) {
              selectedIndexes.splice(selectedIndex, 1);
              props.onChange(selectedIndexes);
            } else {
              if (!(selectedIndexes.length >= props.maxSelectable)) {
                selectedIndexes.push(index);
                props.onChange(selectedIndexes);
              }
            }
            return {
              selected: selectedIndexes
            };
          } else {
            props.onChange(index);
            return {
              selected: index
            }
          }
        });
      }
    render() {
        console.log("this.props.graphSpec:",this.props.graphSpec)
        const galleryItems = this.props.graphSpec.map((item,idx) =>
                <div key={idx.toString()}
                     className="graph-container"
                     id={"graph-container-".concat(idx.toString())}>
                    <SelectableCard key={idx} 
                        selected={this.state.selected.indexOf(idx) > -1 } 
                        onClick={(e) => this.onItemSelected(idx)}>
                            <VegaLite spec={item}  
                                    padding={{left: 10, top: 5, right: 5, bottom: 5}}
                                    actions={false} />
                    </SelectableCard>
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