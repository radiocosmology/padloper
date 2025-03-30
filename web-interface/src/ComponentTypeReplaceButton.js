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
import EditIcon from '@mui/icons-material/Edit';
import styled from '@mui/material/styles/styled';
import ErrorMessage from './ErrorMessage';

/**
 * A MUI component representing a button for replacing a component type.
 */
const ReplaceButton = styled((props) => (
    <Button 
    style={{
        maxWidth: '40px', 
        maxHeight: '25px', 
        minWidth: '30px', 
        minHeight: '30px',
        marginLeft:'10px'
    }}
    {...props}
        variant="outlined">
        <EditIcon/>
    </Button>
))(({ theme }) => ({
    
}))

export default function ComponentTypeReplaceButton ({toggleReload,name}) {

  // Opens and closes the pop up form.
  const [open, setOpen] = React.useState(false);

  // Stores the name of the new component type.
  const [componentType,setComponentType] = useState('')

  // Stores the comments assocaited with the new component type.
  const [comment,setComment] = useState('')

  // Whether the submit button has been clicked or not.
  const [loading, setLoading] = useState(false);

  /*
  To display error when a user fails to replace a component type.
   */
  const [errorData,setErrorData] = useState(null)

  const handleClickOpen = () => {
    setOpen(true);
  };


  /*
   Function that sets the relevant states back to default once the dialog box is closed or the user clicks on the cancel button.
   
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
      let input = `/api/replace_component_type`;
      input += `?name=${componentType}`;
      input += `&comments=${comment}`;
      input += `&component_type=${name}`;
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
        <ReplaceButton onClick={handleClickOpen}/>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Replace Component Type '{name}'</DialogTitle>
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
