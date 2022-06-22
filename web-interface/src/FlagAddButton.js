import React, { useState } from 'react';


import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import axios from 'axios'
import OutlinedInput from '@mui/material/OutlinedInput';
import Checkbox from '@mui/material/Checkbox';
import ListItemText from '@mui/material/ListItemText';
import ErrorIcon from '@mui/icons-material/Error';


const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};



export default function FlagAddButton ({flag_types,flag_severities,flag_components,elements,toggleReload}){

    // opens and closes the pop up form to add a new flag.
    const [open, setOpen] = useState(false);

    // Stores user inputted values for name of the flag, flag severity selected, flag type selected and comments assocaited with the new flag.
    const [property,setProperty] = useState({
    name: '',
    flag_severity:'',
    flag_type:'',
    comment:''
  })

  // Stores the start time of the flag.
  const [startTime,setStartTime] = useState(0)

  // Stores the end time of the flag.
  const [endTime,setEndTime] = useState(0)

  // Stores the list of component names that are flagged.
  const [componentName,setComponentName] = useState([])

  // Whether the submit button has been clicked or not and set loading to true.
  const [loading, setLoading] = useState(false);

  /*
   To display an error message when a user tried to add a new flag but a flag with the same name already exists in the database.
   */
  const [isError,setIsError] = useState(false)


  // Function that updates the list of component selected by the user in the pop up form.
  const handleChange2 = (event) => {
  const {
        target: { value },
    } = event;
    setComponentName(
        // On autofill we get a stringified value.
        typeof value === 'string' ? value.split(',') : value,
    );
    };

  /*
  Keeps a record of multiple state values.
   */
  const handleChange = (e) =>{
    const name = e.target.name
    const value = e.target.value
    setProperty({...property,[name]:value})
  }

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
    setLoading(false)
    setIsError(false)
    setStartTime(0)
    setEndTime(0)
    setComponentName([])
    setProperty({
    name: '',
    flag_severity:'',
    flag_type:'',
    comment:''
  })
  };

  const flag_components_global_list = [{
    name : 'Global'
  }]

  const handleSubmit = (e) => {
      e.preventDefault() // To preserve the state once the form is submitted.

      if(elements.filter((item)=> item.name === property.name).length === 0){
        let input = `/api/set_flag`;
        input += `?name=${property.name}`;
        input += `&start_time=${startTime}`;
        input += `&end_time=${endTime}`;
        input += `&flag_severity=${property.flag_severity}`;
        input += `&flag_type=${property.flag_type}`;
        input += `&comments=${property.comment}`;
        input += `&flag_components=${componentName.join(';')}`;
        axios.post(input).then((response)=>{
                toggleReload() //To reload the page once the form has been submitted.
                handleClose()
        })
      } else {
          setIsError(true)
      }
  }

  return (
    <>
        <Button variant="contained" onClick={handleClickOpen}>Add Flag</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add A Flag</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
    }}>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Flag"
            type='text'
            fullWidth
            variant="outlined"
            name = 'name'
            value={property.name}
            onChange={handleChange}
            />
    </div>

    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
        <FormControl sx={{width: 300}} >
        <InputLabel id="Flag Type">Flag Type</InputLabel>
        <Select
          labelId="Flag-Type-label"
          id="Flag-Type"
          value={property.flag_type}
          name='flag_type'
          label='Flag Type'
          onChange={handleChange}
         >
          {flag_types.map((item) => {
            return (
              <MenuItem
              key={item.name}
              value={item.name}
              >
              {item.name}
            </MenuItem>
          )}
          )}
        </Select>
      </FormControl>
    </div>
    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
        <FormControl sx={{width: 300}}>
        <InputLabel id="Flag Severity">Flag Severity</InputLabel>
        <Select
          labelId="Flag-Severity-label"
          id="Flag-Severity"
          value={property.flag_severity}
          name = 'flag_severity'
          label='Flag Severity'
          onChange={handleChange}
         >
          {flag_severities.map((item) => {
            return (
              <MenuItem
              key={item.value}
              value={item.value}
              >
              {item.value}
            </MenuItem>
          )}
          )}
        </Select>
      </FormControl>
    </div>
    
    
    <div style={{
        marginTop:'10px'
    }}>
      <FormControl sx={{width: 300}}>
        <InputLabel id="multiple-checkbox-label">Components</InputLabel> 
        <Select
          labelId="multiple-checkbox-label"
          id="multiple-checkbox"
          multiple
          value={componentName}
          onChange={handleChange2}
          input={<OutlinedInput label="Component" />}
          renderValue={(selected) => selected.join(', ')}
          MenuProps={MenuProps}
        >
          {
          componentName.includes('Global') 
          ?
          flag_components_global_list.map((item,index) => (
            <MenuItem 
            key={index} 
            value={item.name}>
              <Checkbox checked={componentName.indexOf(item.name) > -1} />
              <ListItemText primary={item.name} />
            </MenuItem>
          )
          )
          :
          flag_components.map((item,index) => (
            <MenuItem key={index} value={item.name}>
              <Checkbox checked={componentName.indexOf(item.name) > -1} />
              <ListItemText primary={item.name} />
            </MenuItem>
          ))
          }
        </Select>
      </FormControl>
    </div>

    <div style={{
        marginTop:'10px',
    }}>
            <TextField
            required
            margin = 'dense'
            id="start_time"
            label="start_time"
            type="datetime-local"
            sx={{ width: 240 }}
            InputLabelProps={{
                shrink: true,
            }}
            size="large"
            onChange={(event) => {
                let date = new Date(event.target.value);
                setStartTime(Math.round(date.getTime() / 1000));
            }}
                        />
    </div>
    <div style={{
        marginTop:'10px',
    }}>
            <TextField
            required
            margin = 'dense'
            id="end_time"
            label="end_time"
            type="datetime-local"
            sx={{ width: 240 }}
            InputLabelProps={{
                shrink: true,
            }}
            size="large"
            onChange={(event) => {
                let date = new Date(event.target.value);
                setEndTime(Math.round(date.getTime() / 1000));
            }}
                        />
    </div>
    <div style={{
        marginTop:'10px',
        marginBottom:'10px'
    }}>
          <TextField
            margin="dense"
            id="comment"
            label="Comment"
            multiline
            maxRows={4}
            type="text"
            fullWidth
            variant="outlined"
            name = 'comment'
            value={property.comment}
            onChange={handleChange}
            />
    </div>
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
      A flag with the same name already exists in the database
      </>
      : 
      null}
    </div>

        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          {
             componentName.length !== 0 && property.name && property.flag_type && property.flag_severity && startTime && endTime 
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