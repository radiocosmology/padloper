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
import ErrorIcon from '@mui/icons-material/Error';
import axios from 'axios'

export default function FlagTypeAddButton ({toggleReload}) {

  // Opens and closes the pop up form.
  const [open, setOpen] = useState(false);

  // Name of the new flag type to be added.
  const [name,setName] = useState('')

  // Comments associated with the new flag type.
  const [comment,setComment] = useState('')

  // Whether the submit button has been clickd or not.
  const [loading, setLoading] = useState(false);

  /*To display an error message when a user fails to add a new flag type. */
  const [errorData,setErrorData] = useState(null)

  const handleClickOpen = () => {
    setOpen(true);
  };

   /*
  Function that sets the relevant states back to default once the dialog box is closed or the user clicks on the cancel button..
  */
  const handleClose = () => {
    setErrorData(null)
    setOpen(false);
    setLoading(false)
  };

  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.
    setLoading(true)
    let input = `/api/set_flag_type`;
    input += `?name=${name}`;
    input += `&comments=${comment}`;
    axios.post(input).then((response)=>{
      if(response.data.result){
        toggleReload() //To reload the page once the form has been submitted.
        handleClose()
      } else {
        setErrorData(response.data.error)
      }
    })
  }

  return (
    <div>
        <Button variant="contained" onClick={handleClickOpen}>Add Flag Type</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Flag Type</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Flag Type"
            type='text'
            fullWidth
            variant="standard"
            onChange={(e)=>setName(e.target.value)}
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
        errorData
        ?
      <>
      <ErrorIcon
      fontSize='small'
      /> 
      {errorData}
      </>
      :
      null}
    </div>

        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          { name 
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
    </div>
  );
}
