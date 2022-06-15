import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import FlagFilter from './FlagFilter.js';
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import axios from 'axios'
import FormHelperText from '@mui/material/FormHelperText';
import Timestamp from './Timestamp.js';
import OutlinedInput from '@mui/material/OutlinedInput';
import Checkbox from '@mui/material/Checkbox';
import ListItemText from '@mui/material/ListItemText';

/**
 * A MUI component that renders a list of flags.
 */
export default function FlagList() {

    // the list of flag in objects representation
    const [elements, setElements] = useState([]);

    // the first index to show
    const [min, setMin] = useState(0);

    // how many elements there are
    const [count, setCount] = useState(0);

    // the number of elements to show
    const [range, setRange] = useState(100);

    // whether the elements are loaded or not
    const [loaded, setLoaded] = useState(false);

    // property to order the flag types by
    // must be in the set {'name, start_time, end_time'}
    const [orderBy, setOrderBy] = useState('name');

    // how to order the elements
    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

    const [flag_types, setFlagTypes] = useState([]);
    const [flag_severities, setFlagSeverities] = useState([]);
    const [flag_components, setComponents] = useState([{
        name : 'Global'
    }]);

    /* filters stored as 
        [
            {
            name: <str>,
            types: <str>,
            severities: <int>
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
            severity: ""
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
    * "<name>,<ftype_name>,<fseverity_value>;...;<name>,<ftype_name>,<fseverity_value>"
    * @returns Return a string containing all of the filter information
    */
    const createFilterString = () => {

        let strSoFar = "";

        if (filters.length > 0) {

            // create the string 
            for (let f of filters) {
                strSoFar += `${f.name},${f.type},${f.severity};`;
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
    * The function that updates the list of flags when the site is 
    * loaded or a change of the flags is requested 
    * (upon state change).
    */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // create the URL query string
            let input = '/api/flag_list';
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
     * Change the flag count when filters are updated.
     */
    useEffect(() => {
        let input = `/api/flag_count`;
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
     * Load all of the flag types (so they can be used for the filter)
     * 
     * TODO: THIS IS GARBAGE, WILL BE REALLY REALLY SLOW WHEN YOU HAVE A LOT
     * OF FLAG TYPES. INSTEAD, MAKE A FLAG TYPE AUTOCOMPLETE AND
     * THEN USE THEM IN THE FILTERS INSTEAD OF THIS PILE OF TRASH.
     */
    useEffect(() => {

        let input = '/api/flag_type_list'
        input += `?range=0;-1`
        input += `&orderBy=name`
        input += `&orderDirection=asc`
        input += `&nameSubstring=`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setFlagTypes(data.result);
        });
    }, []);

    /**
     * Load all of the flag severities (so they can be used for the filter)
     * 
     * TODO: THIS IS GARBAGE, WILL BE REALLY REALLY SLOW WHEN YOU HAVE A LOT
     * OF FLAG SEVERITIES. INSTEAD, MAKE A FLAG SEVERITY AUTOCOMPLETE AND
     * THEN USE THEM IN THE FILTERS INSTEAD OF THIS PILE OF TRASH.
     */
    useEffect(() => {

        let input = '/api/flag_severity_list'
        input += `?range=0;-1`
        input += `&orderBy=value`
        input += `&orderDirection=asc`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setFlagSeverities(data.result);
        });
    }, []);

    /**
     * Load all of the components (so they can be used for the filter)
     **/
    useEffect(() => {

        let input = '/api/component_list'
        input += `?range=0;-1`
        input += `&orderBy=name`
        input += `&orderDirection=asc`
        fetch(input).then(
            res => res.json()
        ).then(data => {
            setComponents((prevState) => {
                return prevState.concat(data.result)
            });
        });
    }, []);

    // the header cells of the table with their ids, labels, and whether you
    // can order by them.
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Flag',
            allowOrdering: true,
        },
        {
            id: 'start_time', 
            label: 'Start Time',
            allowOrdering: true,
        },
        {
            id: 'end_time', 
            label: 'End Time',
            allowOrdering: false,
        },
        {
            id: 'Type', 
            label: 'Flag Type',
            allowOrdering: false,
        },
        {
            id: 'Severity', 
            label: 'Flag Severity',
            allowOrdering: false,
        },
        {
            id: 'List_of_Components', 
            label: 'List Of Components',
            allowOrdering: false,
        },
        {
            id: 'comments', 
            label: 'Comments',
            allowOrdering: false,
        }
    ];

    /**
     * the rows of the table. We are only putting:
     * - the name,
     * - the start time,
     * - the end time,
     * - flag's allowed types,
     * - flag's allowed severity,
     * - the comments associated with the property type.
     */
    let tableRowContent = elements.map((e) => [
        e.name,
       <Timestamp unixTime={e.start_time}/>,
       <Timestamp unixTime={e.end_time}/>,
        e.flag_type.name,
        e.flag_severity.value,
        e.flag_components != ''
        ? 
        e.flag_components.map((item,index)=>{
                return (
                    <li key={index}>{item}</li>
                )
        })
        :
        'Global',
        e.comments
    ]);

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};


  const FlagAddButton = ({flagTypes,flagSeverities,flagComponents}) => {

    const [open, setOpen] = useState(false);
    const [isError,setIsError] = useState(false)
  const [property,setProperty] = useState({
    name: '',
    flag_severity:'',
    flag_type:'',
    comment:''
  })
  const [startTime,setStartTime] = useState(0)
  const [endTime,setEndTime] = useState(0)
  const [componentName,setComponentName] = useState([])
  const [loading, setLoading] = useState(false);

    const handleChange2 = (event) => {
    const {
        target: { value },
    } = event;
    setComponentName(
        // On autofill we get a stringified value.
        typeof value === 'string' ? value.split(',') : value,
    );
    };

  /*
  Keeps a record of multiple state values.
   */
  const handleChange = (e) =>{
    const name = e.target.name
    const value = e.target.value
    setProperty({...property,[name]:value})
  }

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
    setLoading(false)
    setStartTime(0)
    setEndTime(0)
    setComponentName([])
    setProperty({
    name: '',
    flag_severity:'',
    flag_type:'',
    comment:''
  })
  };

  const flag_components_global_list = [{
    name : 'Global'
  }]

  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.

    /*
    These conditions don't allow the user to submit the form if the property type name, 
    component type, units, allowed regex or number of values fields in the form
    are left empty.
     */
    if(property.name && startTime && endTime && property.flag_severity && property.flag_type){ 
    let input = `/api/set_flag`;
    input += `?name=${property.name}`;
    input += `&start_time=${startTime}`;
    input += `&end_time=${endTime}`;
    input += `&flag_severity=${property.flag_severity}`;
    input += `&flag_type=${property.flag_type}`;
    input += `&comments=${property.comment}`;
    input += `&flag_components=${componentName.join(';')}`;
    axios.post(input).then((response)=>{
            toggleReload() //To reload the page once the form has been submitted.
    })
    } else {
      setIsError(true) 
    }
  }

  return (
    <>
        <Button variant="contained" onClick={handleClickOpen}>Add Flag</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add A Flag</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
    }}>
          <TextField
            error={isError}
            helperText = {isError ? 'Cannot be empty' : ''}
            autoFocus
            margin="dense"
            id="name"
            label="Flag"
            type='text'
            fullWidth
            variant="outlined"
            name = 'name'
            value={property.name}
            onChange={handleChange}
            />
    </div>

    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
        <FormControl sx={{width: 300}} error = {isError}>
        <InputLabel id="Flag Type">Flag Type</InputLabel>
        <Select
          labelId="Flag-Type-label"
          id="Flag-Type"
          value={property.flag_type}
          name='flag_type'
          label='Flag Type'
          onChange={handleChange}
         >
          {flagTypes.map((item) => {
            return (
              <MenuItem
              key={item.name}
              value={item.name}
              >
              {item.name}
            </MenuItem>
          )}
          )}
        </Select>
        {
        isError ? 
        <FormHelperText>Cannot be empty</FormHelperText> 
        : 
        ''
        }
      </FormControl>
    </div>
    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
        <FormControl sx={{width: 300}} error = {isError}>
        <InputLabel id="Flag Severity">Flag Severity</InputLabel>
        <Select
          labelId="Flag-Severity-label"
          id="Flag-Severity"
          value={property.flag_severity}
          name = 'flag_severity'
          label='Flag Severity'
          onChange={handleChange}
         >
          {flagSeverities.map((item) => {
            return (
              <MenuItem
              key={item.value}
              value={item.value}
              >
              {item.value}
            </MenuItem>
          )}
          )}
        </Select>
        {
        isError ? 
        <FormHelperText>Cannot be empty</FormHelperText> 
        : 
        ''
        }
      </FormControl>
    </div>
    
    
    <div style={{
        marginTop:'10px'
    }}>
      <FormControl sx={{width: 300}} error = {isError}>
        <InputLabel id="multiple-checkbox-label">Components</InputLabel> 
        <Select
          labelId="multiple-checkbox-label"
          id="multiple-checkbox"
          multiple
          value={componentName}
          onChange={handleChange2}
          input={<OutlinedInput label="Component" />}
          renderValue={(selected) => selected.join(', ')}
          MenuProps={MenuProps}
        >
          {componentName == 'Global' 
          ?
          flag_components_global_list.map((item,index) => (
            <MenuItem key={index} value={item.name}>
              <Checkbox checked={componentName.indexOf(item.name) > -1} />
              <ListItemText primary={item.name} />
            </MenuItem>
          )
          )
          :
           flagComponents.map((item,index) => (
            <MenuItem key={index} value={item.name}>
              <Checkbox checked={componentName.indexOf(item.name) > -1} />
              <ListItemText primary={item.name} />
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </div>

    <div style={{
        marginTop:'10px',
    }}>
            <TextField
            required
            error={isError}
            helperText={isError ? 'Cannot be empty' : ''}
            margin = 'dense'
            id="start_time"
            label="start_time"
            type="datetime-local"
            sx={{ width: 240 }}
            InputLabelProps={{
                shrink: true,
            }}
            size="large"
            onChange={(event) => {
                let date = new Date(event.target.value);
                setStartTime(Math.round(date.getTime() / 1000));
            }}
                        />
    </div>
    <div style={{
        marginTop:'10px',
    }}>
            <TextField
            required
            error={isError}
            helperText={isError ? 'Cannot be empty' : ''}
            margin = 'dense'
            id="end_time"
            label="end_time"
            type="datetime-local"
            sx={{ width: 240 }}
            InputLabelProps={{
                shrink: true,
            }}
            size="large"
            onChange={(event) => {
                let date = new Date(event.target.value);
                setEndTime(Math.round(date.getTime() / 1000));
            }}
                        />
    </div>
    <div style={{
        marginTop:'10px',
        marginBottom:'10px'
    }}>
          <TextField
            margin="dense"
            id="comment"
            label="Comment"
            multiline
            maxRows={4}
            type="text"
            fullWidth
            variant="outlined"
            name = 'comment'
            value={property.comment}
            onChange={handleChange}
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
                width="800px"
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
                    <FlagAddButton flagTypes={flag_types} flagSeverities={flag_severities} flagComponents={flag_components}/>
                }
            />
            {
                filters.map(
                    (filter, index) => (
                        <FlagFilter
                            key={index}
                            width="700px"
                            addFilter={() => { }}
                            removeFilter={removeFilter}
                            changeFilter={changeFilter}
                            filter={filter}
                            index={index}
                            types={flag_types}
                            severities = {flag_severities}
                        />
                    )
                )
            }

            <ElementList
                width="800px"
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