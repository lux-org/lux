import {
  DOMWidgetModel, DOMWidgetView, ISerializers
} from '@jupyter-widgets/base';

import {
  MODULE_NAME, MODULE_VERSION
} from './version';

// Import the CSS
import '../css/widget.css'
// import 'bootstrap/dist/css/bootstrap.min.css';

import * as React from "react";
import * as ReactDOM from "react-dom";

import {Tabs,Tab, Alert} from 'react-bootstrap';
// import { useAlert } from "react-alert";
// import TabComponent from './tab';
import ChartGalleryComponent from './chartGallery';
import CurrentViewComponent from './currentView';

export class ExampleModel extends DOMWidgetModel {
  defaults() {
    return {...super.defaults(),
      _model_name: ExampleModel.model_name,
      _model_module: ExampleModel.model_module,
      _model_module_version: ExampleModel.model_module_version,
      _view_name: ExampleModel.view_name,
      _view_module: ExampleModel.view_module,
      value : 'Hello World'
    };
  }

  static serializers: ISerializers = {
      ...DOMWidgetModel.serializers,
      // Add any extra serializers here
    }

  static model_name = 'ExampleModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'JupyterWidgetView';   // Set to null if no view
  static view_module = MODULE_NAME;   // Set to null if no view
  
}

export class JupyterWidgetView extends DOMWidgetView {
  initialize(){    
    let view = this;
    interface WidgetProps{
      value:any,
      currentView:object,
      recommendations:any[],
      activeTab:any,
      showAlert:boolean
    }
    class ReactWidget extends React.Component<JupyterWidgetView,WidgetProps> {
      constructor(props:any){
        super(props);
        console.log("view:",props);
        this.state = {
          value: props.model.get("value"),
          currentView :  props.model.get("current_view"),
          recommendations:  props.model.get("recommendations"),
          activeTab: props.activeTab,
          showAlert:false
        }
        console.log("this.state:",this.state)
        // This binding is necessary to make `this` work in the callback
        this.changeHandler = this.changeHandler.bind(this);
        this.handleSelect = this.handleSelect.bind(this);
        this.exportSelection = this.exportSelection.bind(this);
        
      }
  
      onChange(model:any){// called when the variable is changed in the view.model
        this.setState(model.changed);
      }
      componentDidMount(){ //triggered when component is mounted (i.e., when widget first rendered)
        view.listenTo(view.model,"change",this.onChange.bind(this));
      }
      componentDidUpdate(){ //triggered after component is updated
        console.log(view.model.get("value"));
        view.model.save_changes(); // instead of touch (which leads to callback issues), we have to use save_changes
      }
  
      handleSelect(selectedTab) {
        // The active tab must be set into the state so that
        // the Tabs component knows about the change and re-renders.
        this.setState({
          activeTab: selectedTab
        });
      }      
      exportSelection() {
        console.log("export selection")
        this.setState(
          state => ({
            showAlert:true
        }));
        // Expire alert box in 7 seconds
        setTimeout(()=>{
          this.setState(
                state => ({
                  showAlert:false
           }));
        },7000);
  
      }
      render(){
        console.log("this.state.activeTab:",this.state.activeTab)
        const tabItems = this.state.recommendations.map((actionResult,idx) =>
          <Tab eventKey={actionResult.action} title={actionResult.action} >
            <ChartGalleryComponent graphSpec={actionResult.vspec}/> 
          </Tab>);
        let alertBtn;
        if (this.state.showAlert){
          alertBtn= <Alert id="alertBox" 
                           key="infoAlert" 
                           variant="info" 
                           dismissible>
            Exported selected visualizations to Python variable `widget.selectedVis`
          </Alert>
        }
        return (<div id="widgetContainer">
                  <CurrentViewComponent currentViewSpec={this.state.currentView}/>
                  <div id="tabBanner">
                    <Tabs activeKey={this.state.activeTab} id="tabBannerList" onSelect={this.handleSelect}>
                      {tabItems}
                    </Tabs>
                  </div>
                  <i  id="exportBtn" 
                      className='fa fa-upload' 
                      title='Export selected visualization into variable'
                      onClick={this.exportSelection}
                  />
                  {alertBtn}                  
                </div>);
      }
      changeHandler(event:any){
        var inputVal = event.target.value
        this.setState(state => ({
          value: inputVal
        }));
        view.model.set('value',inputVal);
      }
    }
    const $app = document.createElement("div");
    const App = React.createElement(ReactWidget,view);
    ReactDOM.render(App,$app);
    view.el.append($app);
  }
}