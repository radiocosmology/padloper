import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import ComponentFilter from './ComponentFilter.js';
import { Link } from "react-router-dom";
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';

import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import axios from 'axios'
import { styled } from '@mui/material/styles';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';


/**
 * A MUI component that represents a list of components.
 */
function ComponentList() {

    // the list of components in objects representation
    const [components, setComponents] = useState([]);

    // the first component index to show
    const [min, setMin] = useState(0);

    // how many components there are
    const [count, setCount] = useState(0);

    // the number of components to show
    const [range, setRange] = useState(100);

    // whether the components are loaded or not
    const [loaded, setLoaded] = useState(false);

    // initialized to store unique component revision names
    const [componentRevisionNameList,setComponentRevisionNameList] = useState([])

    // property to order the components by.
    // must be in the set {'name', 'type', 'revision'}
    const [orderBy, setOrderBy] = useState('name');

    /*
    stores component types as
    [
        {
        'name': <str>
        'revisions': [
            <revision name as str>,
            ...,
            <revision name as str>
        ]
        }
    ]
    */
    const [types_and_revisions,
        setTypesAndRevisions] = useState([]);

    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

    /* filters stored as 
    [
    {
    name: <str>,
    type: <str>,
    revision: <str>
    }
    ]
    */
    const [filters, setFilters] = useState([]);

    // add an empty filter to filters
    const addFilter = () => {
        setFilters([...filters, {
            name: "",
            type: "",
            revision: ""
        }])
    }

    /* 
    Remove a filter at some index.
    index is an integer s.t. 0 <= index < filters.length
    */
    const removeFilter = (index) => {
        if (index >= 0 && index < filters.length) {
            let newFilters = filters.filter((element, i) => index !== i);
            setFilters(newFilters);
        }
    }

    /* 
    Change the filter at index :index: to :newFilter:.
    index is an integer s.t. 0 <= index < filters.length
    */
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

    /*
    To send the filters to the URL, create a string that contains all the
    filter information.

    The string is of the format
    "<name>,<ctype_name>,<rev_name>;...;<name>,<ctype_name>,<rev_name>"

    */
    const createFilterString = () => {

        let strSoFar = "";

        if (filters.length > 0) {

            // create the string 
            for (let f of filters) {
                strSoFar += `${f.name},${f.type},${f.revision};`;
            }

            // remove the last semicolon.
            strSoFar = strSoFar.substring(0, strSoFar.length - 1);
        }

        return strSoFar;
    }

    // Update the state after a new component is submitted via the pop up form.
    const [reloadBool, setReloadBool] = useState(false);
    function toggleReload() {
        setReloadBool(!reloadBool);
    }

    /*
    The function that updates the list of components when the site is loaded
    or a change of the components is requested (upon state change).
    */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // create the URL query string
            let input = '/api/component_list'
            input += `?range=${min};${min + range}`
            input += `&orderBy=${orderBy}`
            input += `&orderDirection=${orderDirection}`
            if (filters.length > 0) {
                input += `&filters=${createFilterString()}`;
            }
    
            // query the URL with flask, and set the input.
            fetch(input).then(
                res => res.json()
            ).then(data => {
                setComponents(data.result);
                setLoaded(true);
            });
        }
        fetchData();
    }, [
        min,
        range,
        orderBy,
        orderDirection,
        filters,
        reloadBool
    ]
    );

    /*
    function to change the component count when filters are updated.
    */
    useEffect(() => {

        fetch(`/api/component_count?filters=${createFilterString()}`).then(
            res => res.json()
        ).then(data => {
            setCount(data.result);

            setMin(0);
        });
    }, [filters,reloadBool]);

    /*
    When the site is loaded, load all of the component types and revisions.
    */
    useEffect(() => {
        fetch("/api/component_types_and_revisions").then(
            res => res.json()
        ).then(data => {
            setTypesAndRevisions(data.result);
            data.result.map((item)=>{
                setComponentRevisionNameList(prevState => {
                    return (
                        [...prevState,item.revisions[0]]
                    )
                })
            })
        });
    }, []);

    // the header cells of the table with their ids, labels, and how to align
    // them. 
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Component Name',
            allowOrdering: true,
        },
        {
            id: 'type', 
            label: 'Type',
            allowOrdering: true,
        },
        {
            id: 'revision', 
            label: 'Revision',
            allowOrdering: true,
        },
    ];

    // What to display in each row.
    let tableRowContent = components.map(c => [
        <Link to={`/component/${c.name}`}>
            {c.name}
        </Link>,
        c.type.name,
        c.revision.name,
    ]);


  // component that handles adding a new component in the db
  const ComponentAddButton = ({componentRevisionNameList}) => {

  // opens and closes the pop up form.
  const [open, setOpen] = useState(false);

  // controls when to display error messages 
  const [isError,setIsError] = useState(false)

  // stores the component name
  const [name,setName] = useState('')

  // when adding components in bulk, this state stores all
  // the names 
  const [nameList,setNameList] = useState([])

  // stores the component type name selected in the pop up form
  const [componentType,setComponentType] = useState('')

  // stores the component revision name selected in the pop up form
  const [componentRevision,setComponentRevision] = useState('')

  // whether the submit button has been clicked or not
  const [loading, setLoading] = useState(false);

  /*
  Function that selects only unique values from an array.
   */
  const unique = (value, index, self) => {
  return self.indexOf(value) === index
}

  // Style for displaying all the components being selected to add in bulk
  const ListItem = styled('li')(({ theme }) => ({
    margin: theme.spacing(0.5),
    }));
  
  // to increase the key count in the chipData array of objects
  const [keyCount,setKeyCount] = useState(1)

  // dummy array containing all the component names to be added 
  const [chipData, setChipData] = useState([
    { key: 0, label: 'Example' },
  ]);

  // handles removing a selected component name in the pop up form
  const handleDelete = (chipToDelete) => () => {
    setChipData((chips) => chips.filter((chip) => chip.key !== chipToDelete.key));
  };
 
  // adds the component name in the chipData array of objects and displays the name on the pop up form
  const handleSubmit2 = (e) => {
    e.preventDefault()
      setChipData((prevState)=>{
        return prevState.concat(
          [
          {
          key: keyCount,
          label : name
        }
      ]
        )
      })
      setKeyCount((prevState)=> prevState + 1)
      setNameList(prevState => {
                    return (
                        [...prevState,name]
                    )
                })
            }


  /*
  Function that is used to open the form when the user clicks
  on the 'add' button.
   */
  const handleClickOpen = () => {
    setOpen(true);
  };

  /*
  Function sets the relevant form variables back to empty string once the form is closed or the user clicks on the cancel button on the pop up form.
  */
  const handleClose = () => {
    setOpen(false);
    setIsError(false)
    setName('')
    setComponentRevision('')
    setComponentType('')
    setLoading(false)
    setChipData([
    { key: 0, label: 'Example' },
  ])
  };


  /*
    Stores the data in terms of url strings and sends the submitted data to the flask server.
   */
  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.

    // Empty component type along with empty component revision cannot be submitted.
    if(name && componentType && componentRevision){ 
    let input = `/api/set_component`;
    input += `?name=${nameList.join(';')}`;
    input += `&type=${componentType}`;
    input += `&revision=${componentRevision}`;
    axios.post(input).then((response)=>{
                toggleReload() //To reload the list of components once the form has been submitted.
    })
    } else {
      setIsError(true) // Displays the error if empty values of component type or component revision is submitted.
    }
  }

  return (
    <>
        <Button variant="contained" onClick={handleClickOpen}>Add Component</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Component</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
        marginBottom:'10px',
    }}>
    <Paper
    style={{
        marginBottom: '10px'
    }}
      sx={{
        display: 'flex',
        justifyContent: 'center',
        flexWrap: 'wrap',
        listStyle: 'none',
        p: 0.5,
        m: 0,
      }}
      component="ul"
    >
      {chipData.map((data) => {
      return (
          <ListItem key={data.key}>
            <Chip
              label={data.label}
              onDelete={data.label === 'Example' ? undefined : handleDelete(data)}
            />
          </ListItem>
        );
      })}
    </Paper>
      <TextField
            error={isError}
            autoFocus
            margin="dense"
            id="name"
            label="Component Name"
            type='text'
            fullWidth
            variant="outlined"
            onChange={(e)=>setName(e.target.value)}
            helperText = {isError ? 'Cannot be empty' : ''}
            />
            <div style={{
                display:'flex',
                alignItems:'center',
                justifyContent: 'center',
            }}>
      <Button  
      style={{
          marginTop: '10px'
        }}
        variant = 'contained'
        onClick={handleSubmit2}>Add</Button>
        </div>
    </div>

    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
            <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth>
        <InputLabel id="Component Type">
            Component Revision</InputLabel>
        <Select
          labelId="ComponentRevision"
          id="ComponentRevision"
          value={componentRevision}
          label="Component Revision"
          onChange={(e)=>setComponentRevision(e.target.value)}
          >
            {/*
            .filter(Boolean) because some component types don't have a component revision so .filter(Boolean) gets rid of
            undefined values and .includes() can be used.
            */}
            {componentRevisionNameList.filter(Boolean).filter(unique).map((name,index)=>{
                return (
                    <MenuItem key={index} value={name}>{name}
                    </MenuItem>
                    )
                })}
        </Select>
      </FormControl>
    </Box>
    </div>

    {componentRevision ? 
    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
            <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth >
        <InputLabel id="Component Type">
            Component type</InputLabel>
        <Select
          labelId="ComponentType"
          id="ComponentType"
          value={componentType}
          label="Component Type"
          onChange={(e)=>setComponentType(e.target.value)}
          >
            {types_and_revisions.filter(
                element => element.revisions[0]
                ?
                element.revisions[0].includes(String(componentRevision))
                :
                null
                ).map((item,index)=>{
                return (
                    <MenuItem key={index} value={item.name}>{item.name}
                    </MenuItem>
                    )
                })}
        </Select>
      </FormControl>
    </Box>
    </div>
    :
    null}
    
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit}>
              {loading ? <CircularProgress
                            size={24}
                            sx={{
                                color: 'blue',
                            }}
                        /> : "Submit"}
              </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

    return (
        <>
            <ElementRangePanel
                min={min}
                updateMin={(n) => { setMin(n) }}
                range={range}
                updateRange={(n) => { setRange(n) }}
                count={count}
                rightColumn={
                    (
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={addFilter}
                        >
                            Add Filter
                        </Button>
                    )
                }
                rightColumn2 = {<ComponentAddButton componentRevisionNameList={componentRevisionNameList}/>}
            />

            {
                filters.map(
                    (filter, index) => (
                        <ComponentFilter
                            key={index}
                            addFilter={() => { }}
                            removeFilter={removeFilter}
                            changeFilter={changeFilter}
                            filter={filter}
                            index={index}
                            types_and_revisions={types_and_revisions}
                        />
                    )
                )
            }

            <ElementList
                tableRowContent={tableRowContent}
                loaded={loaded}
                orderBy={orderBy}
                direction={orderDirection}
                setOrderBy={setOrderBy}
                setOrderDirection={setOrderDirection}
                tableHeadCells={tableHeadCells}
            />
        </>

    )
}

export default ComponentList;