import React, { useState, useEffect } from 'react';
import { Button, AppBar, Toolbar, IconButton, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import './App.css';

import ComponentList from './ComponentList.js';
import ComponentPage from './ComponentPage.js';

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

        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" className={classes.title}>
              HIRAX Layout DB
            </Typography>
          </Toolbar>
        </AppBar>

        <Switch>
          <Route exact={true} path="/">
            <ComponentList />
          </Route>
          <Route path="/component/:name">
            <h3>
              <ComponentPage />
            </h3>
          </Route>
        </Switch>

      </Router>

    </div>
  );
}

export default App;
