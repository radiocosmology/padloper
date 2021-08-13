import React, { useState, useEffect } from 'react';
import { Button, AppBar, Toolbar, IconButton, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Menu } from '@material-ui/icons';
import './App.css';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import ElementFilter from './ElementFilter.js';

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

  const [components_orderBy, setComponentsOrderBy] = useState('name');

  const [component_types_and_revisions, 
         setComponentTypesAndRevisions] = useState([]);

  // 'asc' or 'desc'
  const [components_orderDirection,
         setComponentsOrderDirection] = useState('asc');

  const [filters, setFilters] = useState([]);

  const addFilter = () => {
    setFilters([...filters, {
      name: "", 
      component_type: "",
      revision: ""
    }])
  }

  const removeFilter = (index) => {
    if (index >= 0 && index < filters.length) {
      let newFilters = filters.filter((element, i) => index != i)
      setFilters(newFilters)
    }
  }

  const changeFilter = (index, newFilter) => {
    if (index >= 0 && index < filters.length) {
      // make a shallow copy of the filters
      let filters_copy = [...filters];

      // set the element at index to the new filter
      filters_copy[index] = newFilter;

      // update the state array
      setFilters(filters_copy);
    }
  }

  const createFilterString = () => {

    let strSoFar = "";

    if (filters.length > 0) {
      
      for (let f of filters) {
        strSoFar += `${f.name},${f.component_type},${f.revision};`;
      }

      strSoFar = strSoFar.substring(0, strSoFar.length - 1);
    }

    return strSoFar;
  }

  useEffect(() => {

    setComponentsLoaded(false);

    let input = '/api/component_list'
    input += `?range=${component_min};${component_min+component_range}`
    input += `&orderBy=${components_orderBy}`
    input += `&orderDirection=${components_orderDirection}`
    if (filters.length > 0) {
      input += `&filters=${createFilterString()}`;
    }

    fetch(input).then(
        res => res.json()
      ).then(data => {
      setComponents(data.result);

      setComponentsLoaded(true);
    });

    }, [
        component_min, 
        component_range, 
        components_orderBy, 
        components_orderDirection,
        filters
      ]
  );

  useEffect(() => {

    fetch(`/api/component_count?filters=${createFilterString()}`).then(
        res => res.json()
      ).then(data => {
      setComponentCount(data.result);
    });
  }, [filters]);

  useEffect(() => {
    fetch("/api/component_types_and_revisions").then(
      res => res.json()
    ).then(data => {
      setComponentTypesAndRevisions(data.result);
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
        addFilter={addFilter}
      />

      {
        filters.map(
          (filter, index) => (
            <ElementFilter 
              addFilter={() => {}}
              removeFilter={removeFilter}
              changeFilter={changeFilter}
              filter={filter}
              index={index}
              types_and_revisions={component_types_and_revisions}
            />
          )
        )
      }

      <ElementList 
        components={components} 
        loaded={components_loaded}
        orderBy={components_orderBy}
        direction={components_orderDirection}
        setOrderBy={setComponentsOrderBy}
        setOrderDirection={setComponentsOrderDirection}
         />

    </div>
  );
}

export default App;
