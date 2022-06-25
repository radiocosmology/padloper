import React, { useState } from 'react';

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
import ErrorIcon from '@mui/icons-material/Error';

export default function ComponentTypeAddButton ({toggleReload}) {

  // Opens and closes the pop up form.
  const [open, setOpen] = React.useState(false);

  // Stores the name of the new component type.
  const [componentType,setComponentType] = useState('')

  // Stores the comments assocaited with the new component type.
  const [comment,setComment] = useState('')

  // Whether the submit button has been clicked or not.
  const [loading, setLoading] = useState(false);

  /*
  To display error when a user tries to add a new component type but a component type with the same name already exists in the database.
   */
  const [isError,setIsError] = useState(false)

  const handleClickOpen = () => {
    setOpen(true);
  };


  /*
   Function that sets the relevant form variables back to empty strings once the form is closed or the user clicks on the cancel button on the pop up form.
   
   */
  const handleClose = () => {
    setComment('')
    setIsError(false)
    setComponentType('')
    setOpen(false);
    setLoading(false)
    setIsError(false)
  };

  const handleSubmit = (e) => {
      e.preventDefault() // To preserve the state once the form is submitted.
      
      let input = `/api/set_component_type`;
      input += `?name=${componentType}`;
      input += `&comments=${comment}`;
      axios.post(input).then((response)=>{
        handleClose()
        toggleReload() //To reload the page once the form has been submitted.
      }).catch(error=> {
        if(error.message === 'Request failed with status code 500'){
          setIsError(true)
        }
      })
  }

  return (
    <div>
        <Button variant="contained" onClick={handleClickOpen}>Add Component Type</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Component Type</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="Component Type"
            label="Component Type"
            type='text'
            fullWidth
            variant="standard"
            onChange={(e)=>setComponentType(e.target.value)}
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
           <div 
    style={{
    marginTop:'15px',
    marginBottom:'5px',
    color:'red',
    display:'flex',
    alignItems:'center'
    }}>
      {
      isError 
      ? 
      <>
      <ErrorIcon
      fontSize='small'
      /> 
      A component type with the same name already exists in the database
      </>
      : 
      null}
    </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          {
            componentType 
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
              </Button>}
        </DialogActions>
      </Dialog>
    </div>
  );
}
