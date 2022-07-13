import React, { useState } from 'react';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContentText from '@mui/material/DialogContentText';

export default function AlertDialog ({handleSubmit,nameList,componentVersion,componentType,loading,alertOpen,handleAlertClose,handleClickAlertOpen}){

  return (
    <div>
        { nameList && componentType 
        ?
          <Button 
        onClick={handleClickAlertOpen}
        >
              Submit
        </Button>
      :
        <Button 
        disabled
        >
              Submit
        </Button>
      }
      <Dialog
        open={alertOpen}
        onClose={handleAlertClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {"Confirmation"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            You are about add components:[{nameList.join(',')}] with component type : [{componentType}] and component version : [{componentVersion}]. Do you Agree ?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleAlertClose}>Disagree</Button>
          <Button onClick={handleSubmit} autoFocus>
            {loading ? <CircularProgress
                            size={24}
                            sx={{
                                color: 'blue',
                            }}
                        /> : 'Agree'}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
  }
