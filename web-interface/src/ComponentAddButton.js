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
import { styled } from '@mui/material/styles';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import AlertDialog from './ComponentAlertDialog.js';
import ErrorIcon from '@mui/icons-material/Error';


  export default function ComponentAddButton ({types_and_versions,components,toggleReload}){

  // opens and closes the pop up form.
  const [open, setOpen] = useState(false);

  // Cannot add a component without a name
  const [componentNameError,setComponentNameError] = useState(false)

  // stores the component name
  const [name,setName] = useState('')

  // when adding components in bulk, this state stores all
  // the names 
  const [nameList,setNameList] = useState([])

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
  Used to open the alert dialog box when the submit button is clicked.
  */
  const [alertOpen, setAlertOpen] = useState(false);

  /*
  Function that is used to open the alert dialog box when the user clicks on the 'submit' button in the form.
  */
  const handleClickAlertOpen = () => {
        setAlertOpen(true)
    };

  /*Function that closes the alert dialog box*/
  const handleAlertClose = () => {
    setAlertOpen(false);
  };


  // Style for displaying all the components being selected to add in bulk
  const ListItem = styled('li')(({ theme }) => ({
    margin: theme.spacing(0.5),
    }));
  
  // to increase the key count in the chipData array of objects
  const [keyCount,setKeyCount] = useState(1)

  // dummy array containing all the component names to be added 
  const [chipData, setChipData] = useState([
    { key: 0, label: 'i.e. ANT0001' },
  ]);

  // handles removing a selected component name in the pop up form
  const handleDelete = (chipToDelete) => () => {
    setChipData((chips) => chips.filter((chip) => chip.key !== chipToDelete.key));
  };
 
  // adds the component name in the chipData array of objects and displays the name on the pop up form
  const handleSubmit2 = () => {
      if(name){
          setComponentNameError(false)
          setIsError(false)
          setChipData((prevState)=>{
            return prevState.concat(
              [
              {
              key: keyCount,
              label : name
            }
          ]
            )
          })
          setKeyCount((prevState)=> prevState + 1)
          setNameList(prevState => {
                        return (
                            [...prevState,name]
                        )
                    })
      } else {
        setComponentNameError(true)
      }
            }


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
    setName('')
    setComponentVersion('')
    setComponentType('')
    setLoading(false)
    setNameList([])
    setChipData([
    { key: 0, label: 'i.e. ANT0001' },
  ])
  };

  /*
    Stores the data in terms of url strings and sends the submitted data to the flask server.
   */
  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.
    let input = `/api/set_component`;
    input += `?name=${nameList.sort().join(';')}`;
    input += `&type=${componentType}`;
    input += `&version=${componentVersion}`;
    axios.post(input).then((response)=>{
                toggleReload() //To reload the list of components once the form has been submitted.
                handleClose()
    }).catch(error => {
      if(error.message === 'Request failed with status code 500'){
        setIsError(true)
        handleAlertClose()
      }
    })

  }
  
  return (
    <>
        <Button variant="contained" onClick={handleClickOpen}>Add Component</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Component</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
        marginBottom:'10px',
    }}>
    <Paper
    style={{
        marginBottom: '10px'
    }}
      sx={{
        display: 'flex',
        justifyContent: 'center',
        flexWrap: 'wrap',
        listStyle: 'none',
        p: 0.5,
        m: 0,
      }}
      component="ul"
    >
      {chipData.map((data) => {
      return (
          <ListItem key={data.key}>
            <Chip
              label={data.label}
              onDelete={data.label === 'i.e. ANT0001' ? undefined : handleDelete(data)}
            />
          </ListItem>
        );
      })}
    </Paper>
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
            <div style={{
                display:'flex',
                alignItems:'center',
                justifyContent: 'center',
            }}>
      <Button  
      style={{
          marginTop: '10px'
        }}
        variant = 'contained'
        onClick={handleSubmit2}
        >Add
        </Button>
        </div>
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
      Components with names: {
        nameList.map((item)=>{
          return (
            components.filter((component)=> component.name === item).map((element)=> 
            {
              return(
                  `[${element.name}]`
              )
            }
            )
            )
        })
      } already exist in the database.
      </>
      : 
      null}
    </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <AlertDialog 
          handleSubmit={handleSubmit}
          nameList={nameList}
          componentVersion={componentVersion}
          componentType={componentType}
          loading={loading}
          alertOpen={alertOpen}
          handleAlertClose={handleAlertClose}
          handleClickAlertOpen={handleClickAlertOpen}
          />
        </DialogActions>
      </Dialog>
    </>
  );
}
