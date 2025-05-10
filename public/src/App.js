import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from '../scripts/home';
import Login from '../scripts/login';
import Register from '../scripts/register';
import CreateClass from '../scripts/create_class';
import ClassLeader from '../scripts/class_leader';
import JoinMeeting from '../scripts/join_meeting';
import Meeting from '../scripts/meeting';
import ClassMember from './scripts/class-member';
import CreateJoinClass from '../scripts/create_join_class';

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
export default App.listen(5000);