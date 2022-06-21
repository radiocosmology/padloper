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

export default function ComponentTypeAddButton ({toggleReload}) {

  const [open, setOpen] = React.useState(false);
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

    // Empty component Type cannot be submitted.
    if(name){ 
    let input = `/api/set_component_type`;
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
        <Button variant="contained" onClick={handleClickOpen}>Add Component Type</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Component Type</DialogTitle>
        <DialogContent>
          <TextField
            error={isError}
            autoFocus
            margin="dense"
            id="name"
            label="Component Type"
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
