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
import FormHelperText from '@mui/material/FormHelperText';
import Button from '@mui/material/Button'
import axios from 'axios'


export default function ComponentRevisionAddButton ({componentTypes,toggleReload}) {
    
  // opens and closes the pop up form to add a new component revision.
  const [open, setOpen] = useState(false);

  // Name of the new component revision.
  const [name,setName] = useState('')

  // Comments associated with the new component revision.
  const [comment,setComment] = useState('')

  // controls when to display error messages.
  const [isError,setIsError] = useState(false)

  // Component type selected while filling the pop up form
  const [inputComponentType,setInputComponentType] = useState('')

  // Whether the submit button has been clicked or not
  const [loading, setLoading] = useState(false);

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
        handleClose()
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