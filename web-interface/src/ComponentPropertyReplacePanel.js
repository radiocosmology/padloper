import React, { useState, useEffect } from 'react';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import MuiTextField from '@mui/material/TextField';

import CloseIcon from '@mui/icons-material/Close';

import ComponentPropertyAutocomplete from './ComponentPropertyAutocomplete.js';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';
import { Typography } from '@mui/material';
import { verifyRegex } from './utility/utility.js';

import moment from "moment";

/**
 * A styled "panel" component, used as the background for the panel.
 * 
 * See https://mui.com/system/styled/ for details on how to make 
 * styled components.
 */
const Panel = styled((props) => (
    <Paper 
        elevation={0}
        {...props}
        sx={{marginTop:1}}
    />
))(({ theme }) => ({
    backgroundColor: 'rgb(240, 240, 255)',
    marginBottom: theme.spacing(2),
    padding: theme.spacing(2),
}));

/**
 * Just a renaming of a filled text field (so no need to type variant="filled"
 * each time)
 */
const TextField = styled((props) => (
    <MuiTextField 
        variant="filled"
        {...props}
    />
))(({ theme }) => ({
}));

/**
 * Close button used in the panel
 */
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


/**
 * The MUI component which represents a panel through which component's properties are
 * replaced.
 * 
 * @param {object} theme - A MUI theme object, see 
 * https://mui.com/material-ui/customization/theming/
 * @param {function} onClose - function to call when the close button is pressed
 * @param {function(string, int, string, string, Array)} onSet - function to 
 * call when replacing a component property.
 * {string} propertyType - the name of the property type
 * {int} time - the time at which to add the property 
 * {string} uid - the ID of the user that is adding the property
 * {string} comments - the comments associated with the property 
 * {Array} values - an array connecting the values of the property. 
 */
function ComponentPropertyReplacePanel(
    {
        theme,
        onClose,
        onSet,
        selected,
        // option,
        // old_uid, 
        // old_comments, 
        oldTextFieldValues,
        oldComments
    }
) {

    // what the "selected" property type is
    const [selectedOption, setSelectedOption] = useState(null);

    // an array of the values of the properties entered in the text fields
    const [textFieldValues, setTextFieldValues] = useState([]);

    /**
     * An array storing the regex matches for each text field. That is, if
     * text field i's value matches the regex needed for the property value,
     * then textFieldAccepted[i] will evaluate to true when treated as
     * a Boolean.
     */
    const [textFieldAccepted, setTextFieldAccepted] = useState([]);

    // Whether all the values in each textfield are accepted.
    const [allValuesAccepted, setAllValuesAccepted] = useState(false);

    // the ID of the user setting the property
    const [uid, setUid] = useState("");

    // the default time to set the property
    // const defaultTime = 1;

    // // time to set the property (NOT the edit time)
    // const [time, setTime] = useState(defaultTime);

    // Default time is now; set the display time and the internal time variable
    // to this to start with.
    const defaultTime = new Date();
    const [time, setTime] = useState(Math.round(defaultTime.getTime() / 1000));
    const [displayTime, setDisplayTime] = useState(defaultTime);
    useEffect(() => {
      setDisplayTime(moment(displayTime).format("YYYY-MM-DD[T]HH:mm:ss"));
    }, []);

    // the comments associated with setting the property
    const [comments, setComments] = useState("");

    // whether the panel is loading: usually happens after the "Connect" button
    // is made, waiting for a response from the DB.
    const [loading, setLoading] = useState(false);

    const [userData, setUserData] = useState({});

    // load previous data
    useEffect(() => {
        setTextFieldValues(oldTextFieldValues);
        setTextFieldAccepted(Array.from({ length: oldTextFieldValues.length }, () => true));
        setComments(oldComments);
    }, [])

    // load user data when the page loads
    useEffect(() => {
        getUserData();
    }, [])

    // set user id
    useEffect(() => {
        if (userData) {
            setUid(userData.login);
        }
    }, [userData])

    /**
     * Get the user data via GitHub
     */
    async function getUserData() {
        await fetch(`${process.env.OAUTH_URL || "http://localhost"}:4000/getUserData`, {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem('accessToken')
            }
            }).then((response) => {
                return response.json();
            }).then((data) => {
                console.log(data);
                setUserData(data);
            });
        }

    /**
     * Check whether a value matches the selected property type's regex.
     * Return false if there is no property type that has been selected.
     * @param {string} value - the value that will be checked 
     * @returns true if value matches the regex, false otherwise.
     */
    function regexCheck(value) {
        if (!selectedOption) {
            return false;
        }
        return verifyRegex(value, selectedOption.allowed_regex);
    }


    /**
     * Select a property type.
     * @param {object} option - the object representing the property type,
     * pulled from the DB. 
     */
    function selectOption(option) {
        
        setSelectedOption(option);

        if (option !== null && option.n_values) {
            // make an empty array of size n_values and fill it 
            // with empty strings
            setTextFieldValues(Array(option.n_values).fill(""));

            // create the textFieldAccepted array.
            let acceptedSoFar = [];
            for (let i = 0; i < option.n_values; i++) {
                acceptedSoFar.push(verifyRegex("", option.allowed_regex));
            }
            setTextFieldAccepted(acceptedSoFar);
        }

    }

    /**
     * Set a value at a specific index of the text field array. This must be
     * done like this because the array is stored in a React state (whoever is
     * reading this, maybe change it to use useRef instead? This doesn't really
     * need to be in a state...)
     * 
     * See https://stackoverflow.com/a/49502115
     * 
     * @param {*} value - The new value
     * @param {int} index - the index of where to change the value
     */
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

    /**
     * Return true if all the text field values match the regex, 
     * false otherwise.
     */
    function checkAllValuesAccepted() {
        for (let a of textFieldAccepted) {
            if (!a) {
                return false;
            }
        }
        return true;
    }

    /**
     * If a text field value changed its accepted state (if it went from
     * accepted to unaccepted, or vice versa), update the "all values accepted"
     * variable.
     */
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
                            Edit the property
                        </Typography>
                    </Grid>

                    <Grid item>
                        <CloseButton onClick={onClose} align="right" />
                    </Grid>
                </Grid>

                <Grid container spacing={2} justifyContent="center">
                    <Grid item>
                        <ComponentPropertyAutocomplete 
                            onSelect={selectOption} 
                            selected={selected}
                        />
                    </Grid>

                    {/* <Grid item>
                        <TextField 
                            required
                            label="User" 
                            sx={{ width: 150 }}
                            onChange={(event) => setUid(event.target.value)}
                        />
                    </Grid> */}

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
                            value={displayTime}
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
                            value={comments}
                        />
                    </Grid>

                </Grid>
                {/* 
                    If a property type has been selected and not all 
                    text field values match the regex, spit out an error.
                */}
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
                        [...Array(+selectedOption.n_values)].map((el, index) => ( 
                            <Grid item key={index}>
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
                                    value={textFieldValues[index]}
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
                        /> : "Update"}
                    </Button>
                </Box>
            </Panel>
        </ThemeProvider>
    )
}

export default ComponentPropertyReplacePanel;