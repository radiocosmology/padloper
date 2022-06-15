import React, { useState, useEffect } from 'react';

import ElementList from './ElementList.js';
import ElementRangePanel from './ElementRangePanel.js';
import { 
    TextField, 
    } 
from '@mui/material';

import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import CircularProgress from '@mui/material/CircularProgress';

import axios from 'axios'

/**
 * A MUI component that renders a list of flag types.
 */
function FlagTypeList() {
    
    // the list of flag types in objects representation
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
    // must be in the set {'name'}
    const [orderBy, setOrderBy] = useState('name');

    // property to order the flag types by
    // must be in the set {'name'}
    const [nameSubstring, setNameSubstring] = useState("");
    
    // how to order the elements
    // 'asc' or 'desc'
    const [orderDirection,
        setOrderDirection] = useState('asc');

        
    const [reloadBool, setReloadBool] = useState(false);
    function toggleReload() {
        setReloadBool(!reloadBool);
    }


    /*
    The function that updates the list of flag types when the site is 
    loaded or a change of the flag types is requested (upon state change).
    */
    useEffect(() => {
        async function fetchData() {
            setLoaded(false);

            // create the URL query string
            let input = '/api/flag_type_list'
            input += `?range=${min};${min + range}`
            input += `&orderBy=${orderBy}`
            input += `&orderDirection=${orderDirection}`
            input += `&nameSubstring=${nameSubstring}`

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
        nameSubstring,
        reloadBool
    ]);

    /**
     * function to change the flag count when filters are updated.
     */
    useEffect(() => {

        fetch(`/api/flag_type_count?nameSubstring=${nameSubstring}`).then(
            res => res.json()
        ).then(data => {
            setCount(data.result);

            setMin(0);
        });
    }, [
        nameSubstring,
        reloadBool
    ]);

    /**
     * The header cells of the table with their ids, labels, and whether you
     * can order by them.
     */
    const tableHeadCells = [
        {
            id: 'name', 
            label: 'Flag Type',
            allowOrdering: true,
        },
        {
            id: 'comments', 
            label: 'Comments',
            allowOrdering: false,
        },
    ];
    /**
     * the rows of the table. We are only putting the name and the comments.
     */
    let tableRowContent = elements.map((e) => [
        e.name,
        e.comments,
    ]);

    const FlagTypeAddButton = () => {

  const [open, setOpen] = useState(false);
  const [name,setName] = useState('')
  const [comment,setComment] = useState('')
  const [isError,setIsError] = useState(false)
  const [loading, setLoading] = useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setIsError(false)
    setLoading(false)
  };

  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.

    // Empty flag Type cannot be submitted.
    if(name){ 
    let input = `/api/set_flag_type`;
    input += `?name=${name}`;
    input += `&comments=${comment}`;
    axios.post(input).then((response)=>{
        toggleReload() //To reload the page once the form has been submitted.
    })
    } else {
      setIsError(true)
    }
  }

  return (
    <div>
        <Button variant="contained" onClick={handleClickOpen}>Add Flag Type</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Flag Type</DialogTitle>
        <DialogContent>
          <TextField
            error={isError}
            autoFocus
            margin="dense"
            id="name"
            label="Flag Type"
            type='text'
            fullWidth
            variant="standard"
            onChange={(e)=>setName(e.target.value)}
            helperText = {name ? '' : 'Cannot be empty'}
          />
          <TextField
            margin="dense"
            id="comment"
            label="Comment"
            type="text"
            fullWidth
            variant="standard"
            onChange={(e)=>setComment(e.target.value)}
          />
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
    </div>
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
                    <TextField 
                        label="Filter by name" 
                        variant="outlined" 
                        onChange={
                            (event) => {
                                setNameSubstring(event.target.value)
                            }
                        }
                    />   
                }
                rightColumn2= {
                    <FlagTypeAddButton/>
                }
                
            />
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

export default FlagTypeList;