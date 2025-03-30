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
import OutlinedInput from '@mui/material/OutlinedInput';
import axios from 'axios'
import ErrorMessage from './ErrorMessage';
import { Checkbox, ListItemText } from '@mui/material';


const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 300,
    },
  },
};



export default function PropertyTypeAddButton ({componentTypes,toggleReload}) {

  // Opens and closes the pop up form.
  const [open, setOpen] = useState(false);

  // Stores the list of component types selected by the user in the pop up form.
  const [componentTypeName, setComponentTypeName] = useState([]);

  // Stores the data inputted by the user/
  const [property,setProperty] = useState({
    name: '',
    units:'',
    allowed_regex:'',
    values:0,
    comment:''
  })

  // Whether the submit button has been clicked or not.
  const [loading, setLoading] = useState(false);

  /*To display an error message when a user fails to add a new property type. */
  const [errorData,setErrorData] = useState(null)


  /*
  Keeps a record of multiple state values.
   */
  const handleChange2 = (e) =>{
    const name = e.target.name
    const value = e.target.value
    setProperty({...property,[name]:value})
  }

  /*This handleChange function is specifically for storing
  multiple values of the allowed component types.
  */
  const handleChange = (event) => {
    const {
      target: { value },
    } = event;
    setComponentTypeName(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value,
    );
  };

  const handleClickOpen = () => {
    setOpen(true);
  };

  /*
  Function that sets the relevant states back to default once the dialog box is closed or the user clicks on the cancel button..
  */
  const handleClose = () => {
    setOpen(false);
    setErrorData(null)
    setLoading(false)
    setComponentTypeName([])
    setProperty({
    name: '',
    units:'',
    allowed_regex:'',
    values:0,
    comment:''
  })
  };

  const handleSubmit = (e) => {
    e.preventDefault() // To preserve the state once the form is submitted.
    setLoading(true)
    let input = `/api/set_property_type`;
    input += `?name=${property.name}`;
    input += `&type=${componentTypeName.join(';')}`;
    input += `&units=${property.units}`;
    input += `&allowed_reg=${encodeURIComponent(property.allowed_regex)}`;
    input += `&values=${property.values}`;
    input += `&comments=${property.comment}`;
    axios.post(input).then((response)=>{
      if(response.data.result){
        toggleReload() //To reload the page once the form has been submitted.
        handleClose()
      } else {
        setErrorData(JSON.parse(response.data.error))
        setLoading(false);
      }
    })
  }

  return (
    <>
        <Button variant="contained" onClick={handleClickOpen}>Add Property Type</Button>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Property Type</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
    }}>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Property Type"
            type='text'
            fullWidth
            variant="outlined"
            name = 'name'
            value={property.name}
            onChange={handleChange2}
            />
    </div>
    <div style={{
        marginTop:'15px',
        marginBottom:'15px',
    }}>   
        <FormControl sx={{width: 300}} >
        <InputLabel id="Allowed Type">Allowed Type</InputLabel>
        <Select
          labelId="multiple-Allowed-Type-label"
          id="multiple-Allowed-Type"
          multiple
          value={componentTypeName}
          onChange={handleChange}
          input={<OutlinedInput id="select-multiple-Allowed-Type" label="Allowed-Type" />}
          renderValue={(selected) => selected.join(',')}
          MenuProps={MenuProps}
        >
          {componentTypes.map((component,index) => (
              <MenuItem
              key={index}
              value={component.name}>
              <Checkbox checked={componentTypeName.indexOf(component.name) > -1} />
              <ListItemText primary={component.name} />
            </MenuItem>
          )
          )}
        </Select>
      </FormControl>
    </div>
    <div style={{
        marginTop:'10px',
    }}>
          <TextField
            margin="dense"
            id="units"
            label="Units"
            type='text'
            fullWidth
            variant="outlined"
            name = 'units'
            value={property.units}
            onChange={handleChange2}
            />
    </div>
    <div style={{
        marginTop:'10px',
        marginBottom:'10px'
    }}>
          <TextField
            margin="dense"
            id="Allowed Regex"
            label="Allowed Regex"
            type='text'
            fullWidth
            variant="outlined"
            name = 'allowed_regex'
            value={property.allowed_regex}
            onChange={handleChange2}
            />
    </div>
    <div style={{
        marginTop:'20px',
        marginBottom:'10px'
    }}>
          <TextField
          id="outlined-number"
          label="Number of Values"
          type="number"
          name = 'values'
          value={property.values}
          onChange={handleChange2}
          InputLabelProps={{
            shrink: true,
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
            onChange={handleChange2}
            />
    </div>
        </DialogContent>
        <ErrorMessage
          style={{marginTop:'5px', marginBottom:'5px'}}
          errorMessage={errorData}
        />
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          { property.name && componentTypeName.length !== 0 && property.allowed_regex && property.values !== 0
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
