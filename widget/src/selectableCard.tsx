import React  from 'react';

class SelectableCard extends React.Component<{selected:boolean,onClick:(any) => void},any> {

  render() {
    var isSelected = this.props.selected ? "selected" : "";
    var className = "selectable " + isSelected;
    return (
      <div className="card">
        <div className={className} onClick={this.props.onClick}>
          {this.props.children}
          <div className="check"><span className="checkmark">✔</span></div>
        </div>
      </div>
    );
  }
}
export default SelectableCard;