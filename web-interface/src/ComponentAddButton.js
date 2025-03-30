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
import Grid from '@mui/material/Grid';
import ErrorMessage from './ErrorMessage.js';

const help_val = 'enter one or more name(s)';
const no_version_val = "– None –";

export default function ComponentAddButton ({types_and_versions,
                                             toggleReload}) {
  // opens and closes the pop up form.
  const [open, setOpen] = useState(false);

  // stores the component name
  const [name, setName] = useState('')

  // when adding components in bulk, this state stores all
  // the names 
  const [nameList, setNameList] = useState([])

  /*
  To display an error message when a user fails to add a new component.
  */
  const [errorData,setErrorData] = useState(null)

  // stores the component type name selected in the pop up form
  const [componentType,setComponentType] = useState('')

  // stores the component version name selected in the pop up form
  const [componentVersion,setComponentVersion] = useState('')

  // List of currently valid versions.
  const [allowedVersions, setAllowedVersions] = useState([]);

  // whether the submit button has been clicked or not
  const [loading, setLoading] = useState(false);

  /*
  Used to open the alert dialog box when the submit button is clicked.
  */
  const [alertOpen, setAlertOpen] = useState(false);

  const updateAllowedVersions = (type) => {
    if (types_and_versions[type].length)
        setAllowedVersions([no_version_val].concat(types_and_versions[type]));
    else
        setAllowedVersions([]);
    setComponentVersion('');
  };

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
    { key: 0, label: help_val},
  ]);

  // handles removing a selected component name in the pop up form
  const handleDelete = (chipToDelete) => () => {
    setChipData((chips) => {
      var ret = chips.filter((chip) => chip.key !== chipToDelete.key);
      setNameList(prevState => {
        return (prevState.filter(s => s!== chipToDelete.label));
      });
      if (ret.length === 0)
          ret = [{key: 0, label: help_val}];
      return ret;
    });
  };
 
  // Adds the component name in the chipData array of objects and displays the
  // name on the pop up form
  const handleAdd = () => {
    var ret;
    setChipData((prevState)=>{
      if (prevState[0].key === 0)
        ret = prevState.slice(1);
      else
        ret = prevState;
      ret = ret.concat([{key: keyCount, label : name}]);
      return ret;
    })
    setKeyCount((prevState) => prevState + 1);
    setNameList(prevState => {return([...prevState,name])});
    setName(prevState => "");
  }


  /*
  Function that is used to open the form when the user clicks
  on the 'add' button.
   */
  const handleClickOpen = () => {
    setOpen(true);
  };

  /*
  Function that sets the relevant states back to default values once the form is closed or the user clicks on the cancel button.
  */
  const handleClose = () => {
    setOpen(false);
    setErrorData(null)
    setName('')
    setComponentVersion('')
    setComponentType('')
    setLoading(false)
    setNameList([])
    setChipData([
    { key: 0, label: help_val },
  ])
  };

  /*
    Stores the data in terms of url strings and sends the submitted data to the flask server.
   */
  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.
    setLoading(true)
    let input = `/api/set_component`;
    input += `?name=${nameList.sort().join(';')}`;
    input += `&type=${componentType}`;
    input += `&version=${componentVersion}`;
    axios.post(input).then((response)=>{
      if(response.data.result){
        toggleReload() //To reload the list of components once the form has been submitted.
        handleClose()
      }
      else{
       setErrorData(JSON.parse(response.data.error))
       handleAlertClose()
      }
        
    })
  }
  
  return (
    <>
    <Button variant="contained" onClick={handleClickOpen}>
      Add Components
    </Button>
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>Add Components</DialogTitle>
      <DialogContent>
      <Paper style={{marginBottom: '10px'}}
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
              <Chip label={data.label}
                    onDelete={data.label === help_val ? undefined : 
                              handleDelete(data)}
              />
            </ListItem>
          );
        })}
      </Paper>
      <Grid container sx={{marginTop: '10px'}} alignItems='stretch' spacing={1}>
        <Grid item>
          <TextField autoFocus id="name" label="Component Name" type='text'
                     variant="outlined" value={name}
                     onChange={(e)=>setName(e.target.value)}
          />
        </Grid><Grid item style={{display: "flex"}}>
          <Button variant = 'contained' onClick={handleAdd} disableElevation
                  disabled = {name === ''}>Add</Button>
        </Grid>
      </Grid>
  
      <Box sx={{marginTop: '10px', minWidth: 120}}>
        <FormControl fullWidth>
          <InputLabel id="Component Type">
              Component Type
          </InputLabel>
          <Select labelId="ComponentType" id="ComponentType"
                  value={componentType} label="Component Type"
                  onChange={(e)=> {setComponentType(e.target.value);
                                   updateAllowedVersions(e.target.value)}}>
            {Object.keys(types_and_versions).map((item)=>{
              return (
                <MenuItem value={item}>{item}
                </MenuItem>
              )
            })}
          </Select>
        </FormControl>
      </Box>
  
      <Box sx={{marginTop: '10px', minWidth: 120}}>
        <FormControl fullWidth >
          <InputLabel id="Component Version">
              {allowedVersions.length === 0 ? 'Version (none available)' :
                                              'Version (optional)'}
          </InputLabel>
          <Select labelId="ComponentVersion" id="ComponentVersion"
                  value={componentVersion} label="Component Version (optional)"
                  onChange={(e)=> setComponentVersion(e.target.value)}
                  disabled={allowedVersions.length === 0}>
            {allowedVersions.map((name) => {
              return (
                <MenuItem value={name == no_version_val ? " " : name}>{name}</MenuItem>
              )
            })}
          </Select>
        </FormControl>
      </Box>
      <ErrorMessage
        style={{marginTop: '10px', marginBottom:'10px'}}
        errorMessage={errorData}
      />
    </DialogContent>
    <DialogActions>
      <Button onClick={handleClose}>Cancel</Button>
      <AlertDialog handleSubmit={handleSubmit} nameList={nameList}
                   componentVersion={componentVersion}
                   componentType={componentType}
                   loading={loading} alertOpen={alertOpen}
                   handleAlertClose={handleAlertClose}
                   handleClickAlertOpen={handleClickAlertOpen}
      />
  </DialogActions>
</Dialog>
</>
);
}
