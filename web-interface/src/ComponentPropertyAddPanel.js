import React, { useState, useEffect } from 'react';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import MuiTextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';

import CloseIcon from '@mui/icons-material/Close';
import PersonIcon from '@mui/icons-material/Person';

import ComponentPropertyAutocomplete from './ComponentPropertyAutocomplete.js';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';
import { Typography } from '@mui/material';
import { verifyRegex } from './utility/utility.js';
import { SettingsSuggestRounded } from '@mui/icons-material';

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
        onClose,
        onSet
    }
) {

    const [selectedOption, setSelectedOption] = useState(null);

    const [textFieldValues, setTextFieldValues] = useState([]);

    const [textFieldAccepted, setTextFieldAccepted] = useState([]);

    const [allValuesAccepted, setAllValuesAccepted] = useState(false);

    const [uid, setUid] = useState("");

    const defaultTime = 1;

    const [time, setTime] = useState(defaultTime);

    const [comments, setComments] = useState("");

    const [loading, setLoading] = useState(false);

    function regexCheck(value) {
        if (!selectedOption) {
            return false;
        }
        return verifyRegex(value, selectedOption.allowed_regex);
    }

    function selectOption(option) {
        setSelectedOption(option);

        if (option !== null && option.n_values) {
            // make an empty array of size n_values and fill it 
            // with empty strings
            setTextFieldValues(Array(option.n_values).fill(""));

            let acceptedSoFar = [];
            for (let i = 0; i < option.n_values; i++) {
                acceptedSoFar.push(verifyRegex("", option.allowed_regex));
            }
            setTextFieldAccepted(acceptedSoFar);
        }

    }

    // https://stackoverflow.com/a/49502115
    function setTextFieldValue(value, index) {

        // make a shallow copy of the filters
        let valuesCopy = [...textFieldValues];
        let acceptedCopy = [...textFieldAccepted];

        // set the element at index to the new filter
        valuesCopy[index] = value;
        acceptedCopy[index] = regexCheck(value);

        // update the state array
        setTextFieldValues(valuesCopy);
        setTextFieldAccepted(acceptedCopy);
    }

    function checkAllValuesAccepted() {
        for (let a of textFieldAccepted) {
            if (!a) {
                return false;
            }
        }
        return true;
    }

    useEffect(() => {
        setAllValuesAccepted(checkAllValuesAccepted());
    }, [textFieldAccepted]);


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
                            required
                            label="User" 
                            sx={{ width: 150 }}
                            onChange={(event) => setUid(event.target.value)}
                        />
                    </Grid>

                    <Grid item>
                        <TextField
                            required
                            id="datetime-local"
                            label="Time"
                            type="datetime-local"
                            sx={{ width: 240 }}
                            InputLabelProps={{
                                shrink: true,
                            }}
                            size="large"
                            onChange={(event) => {
                                let date = new Date(event.target.value);
                                setTime(Math.round(date.getTime() / 1000));
                            }}
                        />
                    </Grid>

                    <Grid item>
                        <TextField
                            id="outlined-multiline-static"
                            label="Comments"
                            multiline
                            sx={{ width: 260 }}
                            onChange={(event) => {
                                setComments(event.target.value)
                            }}
                        />
                    </Grid>

                </Grid>

                {
                    (selectedOption !== null && !allValuesAccepted) ?
                    (<Typography style={{
                        marginTop: theme.spacing(2),
                        color: 'rgba(255,0,0,1)',
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
                        marginTop: theme.spacing(0.4),
                    }}>
                    {(selectedOption !== null) ?
                    (
                        [...Array(selectedOption.n_values)].map((el, index) => ( 
                            <Grid item>
                                <TextField 
                                    required
                                    error={!textFieldAccepted[index]}
                                    helperText={
                                        textFieldAccepted[index] ? ""
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
                        disabled={
                            selectedOption === null || 
                            !allValuesAccepted ||
                            uid === "" ||
                            time === defaultTime    
                        }
                        onClick={
                            () => {
                                setLoading(true);
                                onSet(
                                    selectedOption.name, 
                                    time, 
                                    uid, 
                                    comments, 
                                    textFieldValues
                                );
                            }
                        }
                    >
                        {loading ? 
                        <CircularProgress
                            size={24}
                            sx={{
                                color: 'white',
                            }}
                        /> : "Set"}
                    </Button>
                </Box>
            </Panel>
        </ThemeProvider>
    )
}

export default ComponentPropertyAddPanel;