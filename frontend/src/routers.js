import './App.css';
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import Home from './pages/home';
import NotMatch from './pages/NotMatch';
import { ConfigProvider } from 'antd';
import QualityFailurePage from './pages/AI_expert/Quality';

class PageRouters extends React.Component {
    constructor(props) {
        super(props);
        this.state = {

        };
    }
    render() {
        return (
            <ConfigProvider theme={{
                token: {
                    colorPrimary: 'rgb(88, 153, 206)',
                    borderRadius: 2,
                    colorBgContainer: '#fff'
                }
            }}>
                <BrowserRouter>
                    <Routes>
                        <Route path='/' element={<App />} />
                        {/* <Route path='/login' element={<Login />} /> */}
                        <Route path='/bowayKng' element={<App />}>
                            <Route path='home' element={<Home />} />
                            <Route path='*' element={<NotMatch />} />
                            <Route path='opt1' element={<NotMatch />} />
                            <Route path='opt2' element={<NotMatch />} />
                            <Route path='kg_graph'>
                                <Route path='generalKn' element={<NotMatch />} />
                                <Route path='metalKn' element={<NotMatch />} />
                                <Route path='bowayKn' element={<NotMatch />} />
                            </Route>
                            <Route path='aiExpert'>
                                <Route path='qualities' element={<QualityFailurePage />} />
                                <Route path='__tbd' element={<NotMatch />} />
                            </Route>
                            <Route path='system_settings'>
                                <Route path='system_variables' element={<NotMatch />} />
                                <Route path='user_management' element={<NotMatch />} />
                            </Route>
                        </Route>
                    </Routes>
                </BrowserRouter>
            </ConfigProvider>
        );
    }
}

export default PageRouters;