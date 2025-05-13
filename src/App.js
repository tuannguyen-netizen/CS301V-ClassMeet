import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from '../src/home';
import Login from '../src/index';
import Register from '../src/register';
import CreateClass from '../src/create_class';
import JoinClass from '../src/join_class';
import JoinMeeting from '../src/join_meeting';
import Meeting from './index1';
import ClassMember from '../src/class_member';
import CreateJoinClass from '../src/create_join_class';
import JoinClass from '../src/join_class';

const App = () => {
    return (
        <Router>
            <Switch>
                <Route path="/" exact component={Home} />
                <Route path="/index" component={Login} />
                <Route path="/register" component={Register} />
                <Route path="/create_class" component={CreateClass} />
                <Route path="/join_class" component={JoinClass} />
                <Route path="/join_meeting" component={JoinMeeting} />
                <Route path="/meeting" component={Meeting} />
                <Route path="/class_member" component={ClassMember} />
                <Route path="/create_join_class" component={CreateJoinClass} />
            </Switch>
        </Router>
    );
};

ReactDOM.render(<App />, document.getElementById('root'));
export default App;