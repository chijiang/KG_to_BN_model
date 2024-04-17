import React from "react";
import { Menu } from 'antd';
import { NavLink as Link } from "react-router-dom";

import MenuConfig from "../../config/menuConfig";



class NavLeft extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    // load config
    componentDidMount() {
        const menuTreeNode = this.renderMenu(MenuConfig);
        this.setState({
            menuTreeNode
        })
    }

    // render menue
    renderMenu = (data) => {
        return data.map((item) => {
            if (item.children) {
                return (
                    {
                        key: item.key,
                        label: <Link to={item.key} style={{color: "white", fontWeight: "bold"}}> {item.label} </Link>,
                        icon: item.icon,
                        children: this.renderMenu(item.children)
                    }
                )
            }
            return {
                key: item.key,
                label: <Link to={item.key} style={{color: "white", fontWeight: "bold"}}> {item.label} </Link>,
                icon: item.icon
            }
        })
    }

    render() {
        return (
            <div>
                <Menu
                    className="NaviSider"
                    theme="dark"
                    mode="inline"
                    defaultSelectedKeys={["/bowayKng"]}
                    defaultOpenKeys={["/bowayKng/home"]}
                    items={this.state.menuTreeNode}
                />
            </div>
        );
    }
}

export default NavLeft;