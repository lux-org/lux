import React, { Component } from 'react';
interface toolProps{
    graphIdx:number
}
class ToolComponent extends Component<toolProps,any> {
    constructor(props:toolProps) {
        super(props);
        // This binding is necessary to make `this` work in the callback
        // this.starVis = this.starVis.bind(this);
    }
    // starVis(node){
    //     console.log("starred")
    //     var graphID = parseInt(node.parentElement.id.replace("toolDiv-",""))
    //         var isStarred = node.getAttribute("isStarred") === 'true'
    //         isStarred = !isStarred;
    //         var newLst = current_selected_graphID_list.slice()
    //         if (isStarred){
    //             // Add to list of selected ID
    //             newLst.push(graphID)
    //             node.style.color = "#ffc000"
    //         }else{
    //             //remove starred vis
    //             // TODO modify selected_graphID
    //             var index = newLst.indexOf(graphID);
    //             if (index > -1) {newLst.splice(index, 1);}
    //             node.style.color = "grey"
    //         }
    //         current_selected_graphID_list = newLst
    //         node.setAttribute("isStarred",isStarred)
    //         view.model.set('selected_graphID',newLst)
    //         view.touch()
    // }
    render() {
        let toolDivId = "toolDiv-".concat(this.props.graphIdx.toString())
        return (
            <div className="toolDiv" id ={toolDivId}>
                <i className='fa-check fa' 
                   title='Mark visualization as Selected' 
                //    onClick={(node)=>this.starVis(node)}
                >    
                </i>
            </div>
        );
    }
}
export default ToolComponent;