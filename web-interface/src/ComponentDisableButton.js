import React, { useState } from 'react';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import styled from '@mui/material/styles/styled';
import DeleteIcon from '@mui/icons-material/Delete';
import DialogContentText from '@mui/material/DialogContentText';
import CircularProgress from '@mui/material/CircularProgress';


/*
A MUI component representing a button for disabling.
 */
const DisableButton = styled((props) => (
    <Button 
    style={{
        maxWidth: '40px', 
        maxHeight: '30px', 
        minWidth: '30px', 
        minHeight: '30px',
    }}
    {...props}
        variant="outlined">
        <DeleteIcon/>
    </Button>
))(({ theme }) => ({
    
}))


  export default function DisableAlertDialog ({name,toggleReload}){

  // opens and closes the alert dialog box.
  const [open, setOpen] = useState(false);

  // whether the submit button has been clicked or not
  const [loading, setLoading] = useState(false);

  /*
  Function that is used to open the form when the user clicks
  on the 'disable' button.
   */
  const handleClickOpen = () => {
    setOpen(true);
  };

  /*
  Function that sets the relevant states back to default value once the alert dialog box is closed or the user clicks on the cancel button.
  */
  const handleClose = () => {
    setOpen(false);
    setLoading(false)
  };

    /**
     * Disable a component.
     * @param {string} name - the name of the component which is being disabled.
     * @returns 
     */
    async function handleSubmit(name) {
        setLoading(true)
        // build up the string to query the API
        let input = `/api/disable_component`;
        input += `?name=${name}`;

        return new Promise((resolve, reject) => {
            fetch(input).then(
                res => res.json()
            ).then(data => {
                if (data.result) {
                    toggleReload();
                    handleClose()
                }
                resolve(data.result);
            });
        });

    }
  
  return (
    <>
        <DisableButton onClick={handleClickOpen}/>
      <Dialog 
      open={open} 
      onClose={handleClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{"Confirmation"}</DialogTitle>
        <DialogContent>
            <DialogContentText id="alert-dialog-description">
           You are about to disable component {name}. Do you agree ?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>           
            <Button onClick={()=>{handleSubmit(name)}}>
              {loading ? <CircularProgress
                            size={24}
                            sx={{
                                color: 'blue',
                            }}
                        /> : "Submit"}
              </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

