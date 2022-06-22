import React, { useState } from 'react';

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
import ErrorIcon from '@mui/icons-material/Error';
import Button from '@mui/material/Button'
import axios from 'axios'
import { Typography } from '@mui/material';


export default function ComponentRevisionAddButton ({componentTypes,elements,toggleReload}) {
    
  // opens and closes the pop up form to add a new component revision.
  const [open, setOpen] = useState(false);

  // Name of the new component revision.
  const [componentRevision,setComponentRevision] = useState('')

  // Comments associated with the new component revision.
  const [comment,setComment] = useState('')

  // Component type selected while filling the pop up form
  const [inputComponentType,setInputComponentType] = useState('')

  // Whether the submit button has been clicked or not
  const [loading, setLoading] = useState(false);

  /*
  To display error when a user tries to add a new component revision but a component revision with the same name already exists in the database.
  */
  const [isError,setIsError] = useState(false)

  // Function that opens the form.
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
    setComponentRevision('')
    setIsError(false)
    setComment('')
    setInputComponentType('')
    setLoading(false)
  };


  const handleSubmit = (e) => {
    if(elements.filter((item)=> item.name === componentRevision && item.allowed_type.name === inputComponentType).length === 0){
      e.preventDefault() // To preserve the state once the form is submitted.

      let input = `/api/set_component_revision`;
      input += `?name=${componentRevision}`;
      input += `&type=${inputComponentType}`;
      input += `&comments=${comment}`;
      axios.post(input).then((response)=>{
          toggleReload() //To reload the page once the form has been submitted.
          handleClose()
      })
    }
    else {
      setIsError(true)
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
            autoFocus
            margin="dense"
            id="Component Revision"
            label="Component Revision"
            type='text'
            fullWidth
            variant="outlined"
            onChange={(e)=>setComponentRevision(e.target.value)}
            />
    </div>
    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
            <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth>
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
    <div style={{
        marginTop:'15px',
        marginBottom:'5px',
        color:'red',
        display:'flex',
    }}>
      {isError ? 
      <>
      <ErrorIcon
      fontSize='small'
      /> A component revision with the same name and component type already exists in the database.
      </>
      : 
      null}
    </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          {
            componentRevision && inputComponentType
            ?
          <Button onClick={handleSubmit}>
              {loading ? <CircularProgress
                            size={24}
                            sx={{
                                color: 'blue',
                            }}
                        /> : "Submit"}
              </Button>
              :
              <Button disabled>
                Submit
              </Button>
          }
        </DialogActions>
      </Dialog>
    </>
  );
}