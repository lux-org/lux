import React  from 'react';

class SelectableCard extends React.Component<{label:string,selected:boolean},any> {
  constructor(props:any){
    super(props);
    this.state = {
      selected: this.props.selected,
      selectedLabels :[]
    }
    this.onItemSelected = this.onItemSelected.bind(this);
  }
  onItemSelected() {
    console.log("onItemSelected")
    console.log(this.props.selected)
    
    this.setState(state => ({
      selected: !this.props.selected, 
      selectedLabels: [...this.state.selectedLabels, this.props.label]
    }));
    console.log(this.state)
  }
  render() {
    var isSelected = this.props.selected ? "selected" : "";
    var className = "selectable " + isSelected;
    return (
      <div className="card" onClick={this.onItemSelected}>
        <div className={className}>
          {this.props.children}
          <div className="check"><span className="checkmark">✔</span></div>
        </div>
      </div>
    );
  }
}

class App extends React.Component {
  // onListChanged(selected) {
  //   this.setState({
  //     selected: selected
  //   });
  // }
  render() {
    var title = "title"
    var description = "description"
    // console.log(this.state.selected)
    return (
          <SelectableCard 
            label = {"main"}
            selected={true}
            >
              {/* onChange={this.onListChanged.bind(this)} */}
            <div className="content">
              <h1 className="title">{title}</h1>
              <p className="description">{description}</p>
            </div>
          </SelectableCard>
      );
  }
}



ReactDOM.render(<App/>, document.getElementById("app"));