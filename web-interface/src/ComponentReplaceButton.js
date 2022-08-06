import React, { useState } from 'react';

import Button from '@mui/material/Button';
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
import axios from 'axios'
import ErrorIcon from '@mui/icons-material/Error';
import EditIcon from '@mui/icons-material/Edit';
import styled from '@mui/material/styles/styled';
import CircularProgress from '@mui/material/CircularProgress';

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


  export default function ComponentReplaceButton ({types_and_versions,toggleReload,nameComponent}){

  // opens and closes the pop up form.
  const [open, setOpen] = useState(false);

  // Cannot add a component without a name
  const [componentNameError,setComponentNameError] = useState(false)

  // stores the component name
  const [name,setName] = useState('')

  /*
  To display an error message when a user tries to add a new component but a 
  component with the same name already exists in the database.
  */
  const [isError,setIsError] = useState(false)

  // stores the component type name selected in the pop up form
  const [componentType,setComponentType] = useState('')

  // stores the component version name selected in the pop up form
  const [componentVersion,setComponentVersion] = useState('')

  // whether the submit button has been clicked or not
  const [loading, setLoading] = useState(false);

  /*
  Function that is used to open the form when the user clicks
  on the 'add' button.
   */
  const handleClickOpen = () => {
    setOpen(true);
  };

  /*
  Function that sets the relevant form variables back to empty string once the form is closed or the user clicks on the cancel button on the pop up form.
  */
  const handleClose = () => {
    setOpen(false);
    setComponentNameError(false)
    setIsError(false)
    setComponentVersion('')
    setComponentType('')
    setLoading(false)
  };

  /*
    Stores the data in terms of url strings and sends the submitted data to the flask server.
   */
  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.
    let input = `/api/replace_component`;
    input += `?name=${name}`;
    input += `&type=${componentType}`;
    input += `&version=${componentVersion}`;
    input += `&component=${nameComponent}`;
    axios.post(input).then((response)=>{
                toggleReload() //To reload the list of components once the form has been submitted.
                handleClose()
    }).catch(error => {
      if(error.message === 'Request failed with status code 500'){
        setIsError(true)
      }
    })

  }
  
  return (
    <>
        <ReplaceButton onClick={handleClickOpen}/>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Replace Component '{nameComponent}'</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
        marginBottom:'10px',
    }}>
      <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Component Name"
            type='text'
            fullWidth
            variant="outlined"
            onChange={(e)=>setName(e.target.value)}
            />
    </div>

    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
            <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth>
        <InputLabel id="Component Type">
            Component Type
        </InputLabel>
        <Select
          labelId="ComponentType"
          id="ComponentType"
          value={componentType}
          label="Component Type"
          onChange={(e)=> setComponentType(e.target.value)}
          >
            {types_and_versions.map((item,index)=>{
                return (
                    <MenuItem key={index} value={item.name}>{item.name}
                    </MenuItem>
                    )
                })}
        </Select>
      </FormControl>
    </Box>
    </div>
    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
      <Box sx={{ minWidth: 120 }}>
      <FormControl fullWidth >
        <TextField
          id="ComponentVersion"
          label="Component Version"
          type='text'
          variant='outlined'
          onChange={(e)=> setComponentVersion(e.target.value)}
          >
        </TextField>
      </FormControl>
    </Box>
    </div>

    <div 
    style={{
    marginTop:'15px',
    marginBottom:'5px',
    color:'red',
    display:'flex'
    }}>
      {
      componentNameError ? 
      <>
      <ErrorIcon
      fontSize='small'
      /> 
      Component name cannot be empty
      </> 
      : 
      isError 
      ? 
      <>
      <ErrorIcon
      fontSize='small'
      /> 
      Components with name {name} already exist in the database.
      </>
      : 
      null}
    </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          {
            name && componentType
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
    </>
  );
}
