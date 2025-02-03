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
import ErrorMessage from './ErrorMessage';

export default function ComponentTypeAddButton ({toggleReload}) {

  // Opens and closes the pop up form.
  const [open, setOpen] = useState(false);

  // Stores the name of the new component type.
  const [componentType,setComponentType] = useState('')

  // Stores the comments assocaited with the new component type.
  const [comment,setComment] = useState('')

  // Whether the submit button has been clicked or not.
  const [loading, setLoading] = useState(false);

  /*
  To display error when a user fails to add a new component type.
   */
  const [errorData,setErrorData] = useState(null)

  const handleClickOpen = () => {
    setOpen(true);
  };


  /*
   Function that sets the relevant form variables back to empty strings once the form is closed or the user clicks on the cancel button on the pop up form.
   
   */
  const handleClose = () => {
    setComment('')
    setErrorData(null)
    setComponentType('')
    setOpen(false);
    setLoading(false)
  };

  const handleSubmit = (e) => {
      e.preventDefault() // To preserve the state once the form is submitted.
      setLoading(true)
      let input = `/api/set_component_type`;
      input += `?name=${componentType}`;
      input += `&comments=${comment}`;
      axios.post(input).then((response)=>{
        if(response.data.result){
          handleClose();
          toggleReload(); //To reload the page once the form has been submitted.
        } else {
          setErrorData(JSON.parse(response.data.error));
          setLoading(false);
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
        </DialogContent>
        <ErrorMessage
         style={{marginTop:'5px', marginBottom:'5px'}}
         errorMessage={errorData}
        />
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
