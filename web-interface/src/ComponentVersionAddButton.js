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
import ErrorMessage from './ErrorMessage';


export default function ComponentVersionAddButton ({componentTypes,toggleReload}) {
    
  // opens and closes the pop up form to add a new component version.
  const [open, setOpen] = useState(false);

  // Name of the new component version.
  const [componentVersion,setComponentVersion] = useState('')

  // Comments associated with the new component version.
  const [comment,setComment] = useState('')

  // Component type selected while filling the pop up form
  const [inputComponentType,setInputComponentType] = useState('')

  // Whether the submit button has been clicked or not
  const [loading, setLoading] = useState(false);

  /*
  To display error when a user fails to add a new component version.
  */
  const [errorData,setErrorData] = useState(null)

  // Function that opens the form.
  const handleClickOpen = () => {
    setOpen(true);
  };

  /*
  Function that sets the relevant states back to default once the dialog box is closed or the user clicks on the cancel button.
  */
  const handleClose = () => {
    setOpen(false);
    setComponentVersion('')
    setErrorData(null)
    setComment('')
    setInputComponentType('')
    setLoading(false)
  };


  const handleSubmit = (e) => {
      e.preventDefault() // To preserve the state once the form is submitted.
      setLoading(true)
      let input = `/api/set_component_version`;
      input += `?name=${componentVersion}`;
      input += `&type=${inputComponentType}`;
      input += `&comments=${comment}`;
      axios.post(input).then((response)=>{
        if(response.data.result){
          toggleReload() //To reload the page once the form has been submitted.
          handleClose()
        } else {
          setErrorData(JSON.parse(response.data.error));
          setLoading(false);
        }
      })
  }
  return (
    <>
        <Button variant="contained" onClick={handleClickOpen}>Add Component Version</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Component Version</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
        marginBottom:'10px',
    }}>
          <TextField
            autoFocus
            margin="dense"
            id="Component Version"
            label="Component Version"
            type='text'
            fullWidth
            variant="outlined"
            onChange={(e)=>setComponentVersion(e.target.value)}
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
        </DialogContent>
        <ErrorMessage
          style={{marginTop:'5px', marginBottom:'5px'}}
          errorMessage={errorData}
        />
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          {
            componentVersion && inputComponentType
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
