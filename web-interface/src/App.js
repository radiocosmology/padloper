import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import './App.css';

import ComponentList from './ComponentList.js';
import ComponentPage from './ComponentPage.js';
import Header from './Header.js';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

// styling for the React elements 
const useStyles = makeStyles((theme) => ({
  title: {
    flexGrow: 1,
  },
}));



function App() {

  // load the styles
  const classes = useStyles();


  // return the necessary JSX.
  return (
    <div className="App">
      <Router>

        <Header />

        <Switch>
          <Route exact={true} path="/list/component">
            <ComponentList />
          </Route>
          <Route path="/component/:name">
            <ComponentPage />
          </Route>
        </Switch>

      </Router>

    </div>
  );
}

export default App;
