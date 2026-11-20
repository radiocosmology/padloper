import React, { useState } from 'react';
import axios from 'axios';

import { styled } from '@mui/material/styles';
import {
    Box, Button, Chip, Checkbox, Dialog, DialogActions, DialogContent,
    DialogTitle, FormControl, FormControlLabel, Grid, InputLabel,
    MenuItem, Paper, Select, TextField
} from '@mui/material';

import { withBase } from './paths.js';
import AlertDialog from './ComponentAlertDialog.js';
import ErrorMessage from './ErrorMessage.js';

function ComponentSequenceAddButton({componentTypes, toggleReload}) {
    // opens and closes the pop up form
    const [open, setOpen] = useState(false);

    // store the error data for display if necessary
    const [errorData, setErrorData] = useState(null);

    // stores the component name
    const [name, setName] = useState('');

    // store selected component type
    const [componentType, setComponentType] = useState('');

    // store the format
    const [format, setFormat] = useState('');

    // store the value that determines if we should auto-increment
    const [increment, setIncrement] = useState(false);

    // store the next sequence number with default 0
    const [nextSeq, setNextSeq] = useState(0);

    // whether the submit button has been clicked or not
    const [loading, setLoading] = useState(false);

    // use to open the alert dialog box when the submit button is clicked
    const [alertOpen, setAlertOpen] = useState(false);

    /**
     * Function that is used to open the alert dialog box when the user
     * clicks on the 'submit' button in the form.
     */
    const handleClickAlertOpen = () => {
        setAlertOpen(true);
    };

    /**
     * Function that closes the alert dialog box
     */
    const handleAlertClose = () => {
        setAlertOpen(false);
    };

    /**
     * Function used to open the form when the user clicks the 'add' button
     */
    const handleClickOpen = () => {
        setOpen(true);
    };

    /**
     * Function that sets the relevant states to default when the form is
     * closed or user clicks 'cancel'.
     */
    const handleClose = () => {
        setOpen(false);
        setErrorData(null);
        setName('');
        setComponentType('');
        setLoading(false);
    };

    /**
     * Handle the form submission and send data to flask server.
     */
    const handleSubmit = (e) => {
        e.preventDefault();
        setLoading(true);

        let path = '/api/set_sequence';
        path += `?name=${name}`;
        path += `&component_type=${componentType}`;
        path += `&format=${format}`;
        path += `&increment=${increment}`;
        path += `&next_seq=${nextSeq}`;

        axios.post(withBase(path)).then((res) => {
            if (res?.data?.result) {
                toggleReload();
                handleClose();
            } else {
                setErrorData(JSON.parse(res?.data?.error));
            }
        });
    }

    return (
        <>
            <Button variant="contained" onClick={handleClickOpen}>
                Add Sequence
            </Button>

            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Add Sequence</DialogTitle>
                <DialogContent>
                    <Box sx={{ marginTop: '10px', minWidth: 200 }}>
                        <FormControl fullWidth>
                            <TextField
                                autoFocus
                                id="name"
                                label="Name"
                                type="text"
                                variant="outlined"
                                value={name}
                                onChange={(e) => {
                                    setName(e.target.value);
                                }}
                            />
                        </FormControl>
                    </Box>
                    <Box sx={{ marginTop: '10px', minWidth: 300 }}>
                        <FormControl fullWidth>
                            <InputLabel id="componentTypeLabel">
                                Component Type
                            </InputLabel>
                            <Select
                                labelId="componentTypeLabel"
                                id="componentType"
                                label="Component Type"
                                value={componentType}
                                onChange={(e) => {
                                    setComponentType(e.target.value);
                                }}
                            >
                                {Object.values(componentTypes).map((item) => {
                                    return (
                                        <MenuItem value={item.name}>
                                            {item.name}
                                        </MenuItem>
                                    )
                                })}
                            </Select>
                        </FormControl>
                    </Box>
                    <Box sx={{ marginTop: '10px', minWidth: 300 }}>
                        <FormControl fullWidth>
                            <TextField
                                autoFocus
                                id="format"
                                label="Format"
                                type="text"
                                variant="outlined"
                                value={format}
                                onChange={(e) => {
                                    setFormat(e.target.value);
                                }}
                            />
                        </FormControl>
                    </Box>
                    <Box sx={{ marginTop: '10px', minWidth: 300 }}>
                        <FormControlLabel
                            label="Auto-Increment"
                            control={
                                <Checkbox
                                    checked={increment}
                                    onChange={() => {setIncrement(!increment)}}
                                    slotProps={{
                                        input: { 'aria-label': 'controlled' },
                                    }}
                                />
                            }
                        />
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button
                        onClick={handleSubmit}
                        variant="contained"
                        color="primary"
                    >
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    )
}

export default ComponentSequenceAddButton;
