import React, { useState } from 'react';
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import axios from 'axios'
import styled from '@mui/material/styles/styled';

/**
 * A MUI component representing a button for ending a component's property or connection.
 */
const EndButton = styled((props) => (
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
        End
    </Button>
))(({ theme }) => ({
    
}))



export default function FlagEndButton ({toggleReload,name}){

    // opens and closes the pop up form to add a new flag.
    const [open, setOpen] = useState(false);

    // Stores user inputted values for name of the flag, flag severity selected, flag type selected and comments assocaited with the new flag.
    const [property,setProperty] = useState({
    uid: '',
    comment:''
    })

  // Stores the start time of the flag.
  const [endTime,setEndTime] = useState(0)

  // Whether the submit button has been clicked or not and set loading to true.
  const [loading, setLoading] = useState(false);
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
    setEndTime(0)
    setProperty({
    uid: '',
    comment:''
  })
  };

  const handleSubmit = (e) => {
      e.preventDefault() // To preserve the state once the form is submitted.
      setLoading(true)
      let input = `/api/unset_flag`;
      input += `?name=${name}`;
      input += `&end_time=${endTime}`;
      input += `&uid=${property.uid}`;
      input += `&comments=${property.comment}`;
      axios.post(input).then((response)=>{
              toggleReload() //To reload the page once the form has been submitted.
      })
    } 
  return (
    <>
        <EndButton onClick={handleClickOpen}/>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>End the Flag</DialogTitle>
        <DialogContent>
    <div style={{
        marginTop:'10px',
    }}>
          <TextField
            margin="dense"
            id="uid"
            label="UID"
            type='text'
            fullWidth
            variant="outlined"
            name = 'uid'
            value={property.uid}
            onChange={handleChange}
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
            label="End Comment"
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
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          {
           property.uid && endTime
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