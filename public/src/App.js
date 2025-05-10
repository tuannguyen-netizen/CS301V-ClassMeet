import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from '../src/home';
import Login from '../src/index';
import Register from '../src/register';
import CreateClass from '../src/create_class';
import ClassLeader from '../src/class_leader';
import JoinMeeting from '../src/join_meeting';
import Meeting from '../src/meeting';
import ClassMember from './src/class-member';
import CreateJoinClass from '../src/create_join_class';

const App = () => {
    return (
        <Router>
            <Switch>
                <Route path="/" exact component={Home} />
                <Route path="/login" component={Login} />
                <Route path="/register" component={Register} />
                <Route path="/create_class" component={CreateClass} />
                <Route path="/class_leader" component={ClassLeader} />
                <Route path="/join_meeting" component={JoinMeeting} />
                <Route path="/meeting" component={Meeting} />
                <Route path="/class_member" component={ClassMember} />
                <Route path="/create_join_class" component={CreateJoinClass} />
            </Switch>
        </Router>
    );
};
export default App;