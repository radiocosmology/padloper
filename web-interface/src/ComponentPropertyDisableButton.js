import React, { useState } from 'react';

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Grid from '@mui/material/Grid';
import styled from '@mui/material/styles/styled';
import DeleteIcon from '@mui/icons-material/Delete';
import DialogContentText from '@mui/material/DialogContentText';
import CircularProgress from '@mui/material/CircularProgress';
import ErrorIcon from '@mui/icons-material/Error';
import { Typography } from '@mui/material';

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


  export default function DisableAlertDialog ({name,propertyType,propertyValue,propertyUnit,toggleReload}){

  // opens and closes the alert dialog box.
  const [open, setOpen] = useState(false);

  const [errorMessage, setErrorMessage] = useState(null);

  // whether the submit button has been clicked or not
  const [loading, setLoading] = useState(false);

  /*
  Function that is used to open the form when the user clicks
  on the disable button.
   */
  const handleClickOpen = () => {
    setOpen(true);
  };

  /*
  Function that sets the relevant state back to default value once the alert dialog box is closed or the user clicks on the cancel button.
  */
  const handleClose = () => {
    setOpen(false);
    setLoading(false)
  };

     /**
     * Disable a property.
     * @param {string} propertyName - the name of the property to disable.
     * @returns 
     */
    async function handleSubmit(propertyName) {
        setLoading(true)
        // build up the string to query the API
        let input = `/api/component_disable_property`;
        input += `?name=${name}`;
        input += `&propertyType=${propertyName}`;

        return new Promise((resolve, reject) => {
            fetch(input).then(
                res => res.json()
            ).then(data => {
                if (data.result) {
                    setErrorMessage(null);
                    toggleReload();
                    handleClose()
                }
                else {
                  setErrorMessage(data.error);
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
           You are about to disable property {propertyType} = { '[ ' +
                                        propertyValue.map(
                                            el => el + ` ${
                                            (propertyUnit === undefined) ? 
                                                '' : propertyUnit
                                            }`
                                        ).join(", ") + ' ]'
                                    }. Do you agree ?
          </DialogContentText>
          {errorMessage ? 
                    <Grid 
                        container 
                        spacing={1}
                        justifyContent="center"
                    >
                        <Grid item>
                            <ErrorIcon sx={{color: 'red'}} />
                        </Grid>
                        <Grid item>
                            <Typography
                                style={{
                                    color: 'rgb(255,0,0)',
                                }}
                            >
                                {errorMessage}
                            </Typography>
                        </Grid>
                    </Grid> : <></>
                }
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>           
            <Button onClick={()=>{handleSubmit(propertyType)}}>
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

