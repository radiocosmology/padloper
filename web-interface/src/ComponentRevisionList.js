import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import { 
    Button,
    } 
from '@mui/material';
import ComponentRevisionFilter from './ComponentRevisionFilter.js';
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
import FormHelperText from '@mui/material/FormHelperText';

import axios from 'axios'

/**
 * A MUI component that renders a list of component revisions.
 */
function ComponentRevisionList() {
    
    // the list of component types in objects representation
    const [elements, setElements] = useState([]);

    // the first index to show
    const [min, setMin] = useState(0);

    // how many elements there are
    const [count, setCount] = useState(0);

    // the number of elements to show
    const [range, setRange] = useState(100);

    // whether the elements are loaded or not
    const [loaded, setLoaded] = useState(false);

    // property to order the component types by
    // must be in the set {'name'}
    const [orderBy, setOrderBy] = useState('name');

    // how to order the elements
    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

    // the list of component types
    // TODO: DON'T DO IT LIKE THIS, MAKE A COMPONENT TYPE AUTOCOMPLETE INSTEAD!!
    const [componentTypes, setComponentTypes] = useState([]);

    /* filters stored as 
        [
            {
            name: <str>,
            type: <str>,
            },
            ...
        ]
    */
    const [filters, setFilters] = useState([]);

    /**
     * add an empty filter to filters
     */ 
    const addFilter = () => {
        setFilters([...filters, {
            name: "",
            type: "",
        }])
    }

    /**
     * Remove a filter at some index.
     * @param {int} index - index of the new filter to be removed.
     * 0 <= index < filters.length
     */
    const removeFilter = (index) => {
        if (index >= 0 && index < filters.length) {
            let newFilters = filters.filter((element, i) => index !== i);
            setFilters(newFilters);
        }
    }

    /**
     * Change the filter at index :index: to :newFilter:.
     * @param {int} index - index of the new filter to be changed
     * 0 <= index < filters.length
     **/
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
    
   /**
    * To send the filters to the URL, create a string that contains all the
    * filter information.
    * 
    * The string is of the format
    * "<name>,<ctype_name>;...;<name>,<ctype_name>"
    * @returns Return a string containing all of the filter information
    */
    const createFilterString = () => {

        let strSoFar = "";

        if (filters.length > 0) {

            // create the string 
            for (let f of filters) {
                strSoFar += `${f.name},${f.type};`;
            }

            // remove the last semicolon.
            strSoFar = strSoFar.substring(0, strSoFar.length - 1);
        }

        return strSoFar;
    }

    const [reloadBool, setReloadBool] = useState(false);
    function toggleReload() {
        setReloadBool(!reloadBool);
    }



        
   /**
    * The function that updates the list of component types when the site is 
    * loaded or a change of the component types is requested 
    * (upon state change).
    */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // create the URL query string
            let input = '/api/component_revision_list';
            input += `?range=${min};${min + range}`;
            input += `&orderBy=${orderBy}`;
            input += `&orderDirection=${orderDirection}`;
            if (filters.length > 0) {
                input += `&filters=${createFilterString()}`;
            }

            // query the URL with flask, and set the input.
            fetch(input).then(
                res => res.json()
            ).then(data => {
                setElements(data.result);
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
    ]);

    /**
     * Change the component type count when filters are updated.
     */
    useEffect(() => {
        let input = `/api/component_revision_count`;
        if (filters.length > 0) {
            input += `?filters=${createFilterString()}`;
        }
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setCount(data.result);
            setMin(0);
        });
    }, [
        filters,
        reloadBool
    ]);

    /**
     * Load all of the component types (so they can be used for the filter)
     * 
     * TODO: THIS IS GARBAGE, WILL BE REALLY REALLY SLOW WHEN YOU HAVE A LOT
     * OF COMPONENT TYPES. INSTEAD, MAKE A COMPONENT TYPE AUTOCOMPLETE AND
     * THEN USE THEM IN THE FILTERS INSTEAD OF THIS PILE OF TRASH.
     */
    useEffect(() => {

        let input = '/api/component_type_list'
        input += `?range=0;-1`
        input += `&orderBy=name`
        input += `&orderDirection=asc`
        input += `&nameSubstring=`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setComponentTypes(data.result);
        });
    }, []);

    // the header cells of the table with their ids, labels, and whether you
    // can order by them.
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Component Revision',
            allowOrdering: true,
        },
        {
            id: 'allowed_type', 
            label: 'Allowed Type',
            allowOrdering: true,
        },
        {
            id: 'comments', 
            label: 'Comments',
            allowOrdering: false,
        }
    ];

    /**
     * the rows of the table. We are only putting the name, allowed type of the
     * revision, and the comments.
     */
    let tableRowContent = elements.map((e) => [
        e.name,
        e.allowed_type.name,
        e.comments
    ]);

  const ComponentRevisionAddButton = ({componentTypes}) => {
  const [open, setOpen] = React.useState(false);
  const [name,setName] = useState('')
  const [comment,setComment] = useState('')
  const [isError,setIsError] = useState(false)
  const [inputComponentType,setInputComponentType] = useState('')
  const [loading, setLoading] = useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  /*
  This function sets the variables back to empty string once 
  the form is closed or the user clicks on the cancel button
  on the pop up form.
  */
  const handleClose = () => {
    setOpen(false);
    setIsError(false)
    setName('')
    setComment('')
    setInputComponentType('')
    setLoading(false)
  };


  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.

    // Empty component type along with empty component revision cannot be submitted.
    if(name && inputComponentType){ 
    let input = `/api/set_component_revision`;
    input += `?name=${name}`;
    input += `&type=${inputComponentType}`;
    input += `&comments=${comment}`;
    axios.post(input).then((response)=>{
        toggleReload() //To reload the page once the form has been submitted.
    })
    } else {
      setIsError(true) // Displays the error if empty values of component type or component revision is submitted.
    }
  }

  return (
    <>
        <Button variant="contained" onClick={handleClickOpen}>Add Component Revision</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Component Revision</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
        marginBottom:'10px',
    }}>
          <TextField
            error={isError}
            autoFocus
            margin="dense"
            id="name"
            label="Component Revision"
            type='text'
            fullWidth
            variant="outlined"
            onChange={(e)=>setName(e.target.value)}
            helperText = {isError ? 'Cannot be empty' : ''}
            />
    </div>
    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
            <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth error = {isError}>
        <InputLabel id="Component Type">
            Component Type</InputLabel>
        <Select
          labelId="ComponentType"
          id="ComponentType"
          value={inputComponentType}
          label="Component Type"
          onChange={(e)=>setInputComponentType(e.target.value)}
          >
            {componentTypes.map((component,index)=>{
                return (
                    <MenuItem key={index} value={component.name}>{component.name}
                    </MenuItem>
                    )
                })}
        </Select>
        {
        isError ? 
        <FormHelperText>Cannot be empty</FormHelperText> 
        : 
        ''
        }
      </FormControl>
    </Box>
    </div>
    <div>
          <TextField
            margin="dense"
            id="comment"
            label="Comment"
            multiline
            maxRows={4}
            type="text"
            fullWidth
            variant="outlined"
            onChange={(e)=>setComment(e.target.value)}
            />
    </div>
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
                rightColumn2 = {
                    <ComponentRevisionAddButton componentTypes={componentTypes}/>
                }
            />

            {
                filters.map(
                    (filter, index) => (
                        <ComponentRevisionFilter
                        key={index}
                            addFilter={() => { }}
                            removeFilter={removeFilter}
                            changeFilter={changeFilter}
                            filter={filter}
                            index={index}
                            types={componentTypes}
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

export default ComponentRevisionList;