import React, { useState, useEffect } from 'react';
import { Button, AppBar, Toolbar, IconButton, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Menu } from '@material-ui/icons';
import './App.css';

import ElementList from './ElementList.js';

import ElementRangePanel from './ElementRangePanel.js';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    marginBottom: theme.spacing(1),
  },
  menuButton: {
    marginRight: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
  },
}));

function App() {

  const classes = useStyles();

  const [components, setComponents] = useState([]);

  const [component_min, setComponentMin] = useState(0);

  const [component_count, setComponentCount] = useState(0);

  const [component_range, setComponentRange] = useState(100);

  const [components_loaded, setComponentsLoaded] = useState(false);

  useEffect(() => {

    setComponentsLoaded(false);

    fetch(`/api/component_list?range=${component_min},
      ${component_min+component_range}`).then(
        res => res.json()
      ).then(data => {
      setComponents(data.result);
      setComponentsLoaded(true);
    });
  }, [component_min, component_range]);

  useEffect(() => {

    fetch("/api/component_count").then(
        res => res.json()
      ).then(data => {
      setComponentCount(data.result);
    });
  }, []);

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
            HIRAX Layout DB
          </Typography>
        </Toolbar>
      </AppBar>

      <ElementRangePanel 
        min={component_min} 
        updateMin={(n)=>{setComponentMin(n)}} 
        range={component_range} 
        updateRange={(n)=>{setComponentRange(n)}} 
        count={component_count}
      />

      <ElementList components={components} loaded={components_loaded} />

    </div>
  );
}

export default App;
