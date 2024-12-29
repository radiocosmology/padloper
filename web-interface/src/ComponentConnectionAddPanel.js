import React, { useState, useEffect } from 'react';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import MuiTextField from '@mui/material/TextField';

import CloseIcon from '@mui/icons-material/Close';
import ErrorIcon from '@mui/icons-material/Error';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';
import { Typography } from '@mui/material';
import ComponentAutocomplete from './ComponentAutocomplete.js';

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
        sx={{margin:-1}}
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
 * The MUI component which represents a panel through which connections are
 * added between components.
 * 
 * @param {object} theme - A MUI theme object, see 
 * https://mui.com/material-ui/customization/theming/
 * @param {function} onClose - function to call when the close button is pressed
 * @param {function(string, int, string, string)} onSet - function to call when 
 * setting a component connection. The parameters are of the form:
 * onSet(otherName, time, uid, comments), where otherName is the name of the
 * OTHER component you are connecting this one to, time is the Unix time when
 * the connection is being mdae, uid is the ID of the user making the
 * connection, and comments are the comments associated with the connection.
 * @param {string} name - the name of the component you are connecting another
 * component to.
 */
function ComponentConnectionAddPanel(
    {
        theme,
        onClose,
        onSet,
        name,
        errorConnectionMessage
    }
) {

    // what the "selected" other component is
    const [selectedOption, setSelectedOption] = useState(null);

    // the ID of the user making the connection
    const [uid, setUid] = useState("");

    // Default time is now; set the display time and the internal time variable
    // to this to start with.
    const defaultTime = new Date();
    const [time, setTime] = useState(Math.round(defaultTime.getTime() / 1000));
    const [displayTime, setDisplayTime] = useState(defaultTime);
    useEffect(() => {
      setDisplayTime(moment(displayTime).format("YYYY-MM-DD[T]HH:mm:ss"));
    }, []);

    // When the user changes the time.
    const handleTimeChange = (e) => {
      let date = new Date(e.target.value);
      setTime(Math.round(date.getTime() / 1000));
      setDisplayTime(moment(e.target.value).format("YYYY-MM-DD[T]HH:mm:ss"));
    };

    // comments associated with the connection
    const [comments, setComments] = useState("");

    // whether the panel is loading: usually happens after the "Connect" button
    // is made, waiting for a response from the DB.
    const [loading, setLoading] = useState(false);


    // function to select an option. I'm not even sure why I have this...
    function selectOption(option) {
        setSelectedOption(option);
    }

    const [userData, setUserData] = useState({});

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
        await fetch(`${process.env.OUATH_URL || "http://localhost"}:4000/getUserData`, {
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

    // return the MUI component.
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
                            Connect a component
                        </Typography>
                    </Grid>

                    <Grid item>
                        <CloseButton onClick={onClose} align="right" />
                    </Grid>
                </Grid>

                <Grid container spacing={2} justifyContent="center">
                    <Grid item>
                        <ComponentAutocomplete 
                            onSelect={selectOption} 
                            excludeName={name}
                        />
                    </Grid>

                    {/* <Grid item>
                        <TextField 
                            required
                            label="User" 
                            sx={{ width: 150 }}
                            onChange={(event) => setUid(event.target.value)}
                            value={uid}
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
                            value={displayTime}
                            onChange={(e) => handleTimeChange(e)}
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
                errorConnectionMessage
                ? 
                <Grid 
                container 
                        style={{
                            marginTop: theme.spacing(1),
                        }}
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
                                {errorConnectionMessage}
                            </Typography>
                        </Grid>
                    </Grid> 
                    : 
                    <></>
                }

                

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
                            uid === "" ||
                            time === defaultTime    
                        }
                        onClick={
                            async () => {
                                setLoading(true);
                                onSet(
                                    selectedOption.name, 
                                    time, 
                                    uid, 
                                    comments
                                )
                            }
                        }
                    >
                        {/**
                         * so when the panel is loading, the button
                         * is spinning.
                         */}
                        {loading ? 
                        errorConnectionMessage ?
                        "Set"
                        :
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

export default ComponentConnectionAddPanel;
