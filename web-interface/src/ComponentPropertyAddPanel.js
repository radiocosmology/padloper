import React, { useState, useEffect } from 'react';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import MuiTextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';

import CloseIcon from '@mui/icons-material/Close';
import PersonIcon from '@mui/icons-material/Person';

import ComponentPropertyAutocomplete from './ComponentPropertyAutocomplete.js';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';
import { Typography } from '@mui/material';

const Panel = styled((props) => (
    <Paper 
        elevation={0}
        {...props}
        sx={{margin:-1}}
    />
))(({ theme }) => ({
    backgroundColor: 'rgb(240, 240, 255)',
    marginBottom: theme.spacing(2),
    padding: theme.spacing(2),
}));

const TextField = styled((props) => (
    <MuiTextField 
        variant="filled"
        {...props}
    />
))(({ theme }) => ({
}));

const CloseButton = styled((props) => (
    <Button 
        style={{
            maxWidth: '40px',
            minWidth: '40px',
            maxHeight: '40px',
            minHeight: '40px',
        }}
        {...props}
    >
        <CloseIcon />
    </Button>
))(({ theme }) => ({
}));


function ComponentPropertyAddPanel(
    {
        theme,
        onClose
    }
) {

    const [selectedOption, setSelectedOption] = useState(null);

    const [textFieldValues, setTextFieldValues] = useState([]);

    function selectOption(option) {
        setSelectedOption(option);

        if (option !== null && option.n_values) {
            // make an empty array of size n_values and fill it 
            // with empty strings
            setTextFieldValues(Array(option.n_values).fill(""));
        }

    }


    // https://stackoverflow.com/a/49502115
    function setTextFieldValue(value, index) {
        // make a shallow copy of the filters
        let valuesCopy = [...textFieldValues];

        // set the element at index to the new filter
        valuesCopy[index] = value;

        // update the state array
        setTextFieldValues(valuesCopy);
    }

    function verifyRegex(value) {
        // this ideally should never be called but...
        if (selectedOption === null) {
            return false;
        }
        else {
            return value.match(selectedOption.allowed_regex);
        }
    }

    return (
        <ThemeProvider theme={theme}>
            <Panel>

                <Grid 
                    container 
                    spacing={2} 
                    justifyContent="space-between"
                    style={{
                        marginBottom: theme.spacing(2),
                    }}
                >
                    <Grid item>
                        <Typography style={{
                            color: 'rgba(0,0,0,0.7)',
                        }}>
                            Set a property
                        </Typography>
                    </Grid>

                    <Grid item>
                        <CloseButton onClick={onClose} align="right" />
                    </Grid>
                </Grid>

                <Grid container spacing={2} justifyContent="space-around">
                    <Grid item>
                        <ComponentPropertyAutocomplete 
                            onSelect={selectOption} 
                        />
                    </Grid>

                    <Grid item>
                        <TextField 
                            label="User" 
                            sx={{ width: 150 }}
                        />
                    </Grid>

                    <Grid item>
                        <TextField
                            id="datetime-local"
                            label="Time"
                            type="datetime-local"
                            sx={{ width: 200 }}
                            InputLabelProps={{
                                shrink: true,
                            }}
                            size="large"
                        />
                    </Grid>

                    <Grid item>
                        <TextField
                            id="outlined-multiline-static"
                            label="Comments"
                            multiline
                            sx={{ width: 300 }}
                        />
                    </Grid>

                </Grid>

                {
                    (selectedOption !== null && selectedOption.allowed_regex) ?
                    (<Typography style={{
                        marginTop: theme.spacing(2),
                        color: 'rgba(0,0,0,0.6)',
                    }}>
                        {`Entered values must match 
                        regular expression 
                        ${selectedOption.allowed_regex}`}
                    </Typography>) : ""
                }

                <Grid 
                    container 
                    spacing={2} 
                    justifyContent="center"
                    style={{
                        marginTop: theme.spacing(1),
                    }}>
                    {(selectedOption !== null) ?
                    (
                        [...Array(selectedOption.n_values)].map((el, index) => ( 
                            <Grid item>
                                <TextField 
                                    required
                                    error={!verifyRegex(textFieldValues[index])}
                                    helperText={
                                        verifyRegex(textFieldValues[index]) ? ""
                                        : `Value does not match 
                                        ${selectedOption.allowed_regex}`
                                    }
                                    onChange={
                                        (ev) => {
                                            setTextFieldValue(
                                                ev.target.value, 
                                                index
                                            )
                                        }
                                    }
                                    label={`Value ${index + 1}`}
                                />
                            </Grid>) 
                        )
                    )
                    : ""

                    }
                </Grid>


                <Box 
                    style={{
                        textAlign: "right",
                        marginTop: theme.spacing(2),
                    }}
                >
                    <Button 
                        variant="contained" 
                        size="large"
                        disableElevation
                    >
                        Add
                    </Button>
                </Box>
            </Panel>
        </ThemeProvider>
    )
}

export default ComponentPropertyAddPanel;