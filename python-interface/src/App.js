import React, { useState, useEffect } from 'react';
import { Button, AppBar, Toolbar, IconButton, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Menu } from '@material-ui/icons';
import './App.css';

import ElementList from './ElementList.js';

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

  useEffect(() => {
    fetch("/components_list/&limit=100").then(res => res.json()).then(data => {
      setComponents(data.result);
    });
  }, []);

 // 
  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
            HIRAX Layout DB Hello Adam
          </Typography>
        </Toolbar>
      </AppBar>

      <ElementList components={components} />

    </div>
  );
}

export default App;
