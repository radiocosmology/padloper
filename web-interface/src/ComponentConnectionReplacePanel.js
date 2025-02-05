import React, { useEffect, useState } from 'react';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import MuiTextField from '@mui/material/TextField';
import CloseIcon from '@mui/icons-material/Close';
import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';
import { Typography } from '@mui/material';

import moment from 'moment';
import ErrorMessage from './ErrorMessage';

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
        sx={{marginTop:2}}
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
 * replaced between components.
 * 
 * @param {object} theme - A MUI theme object, see 
 * https://mui.com/material-ui/customization/theming/
 * @param {function} onClose - function to call when the close button is pressed
 * @param {function(string, int, string, string)} onSet - function to call when 
 * replacing a component connection. The parameters are of the form:
 * onSet(otherName, time, uid, comments), time is the Unix time when
 * the connection is being set, uid is the ID of the user setting the
 * connection, and comments are the comments associated with setting the connection.
 */
function ComponentConnectionReplacePanel(
    {
        theme,
        onClose,
        onSet,
        uid,
        conn,
        errorMessage
    }
) {

    // the ID of the user setting the connection
    // const [uid, setUid] = useState("");

    // default time to end the connection
    const defaultTime = new Date();

    // time to make the connection
    const [time, setTime] = useState(defaultTime);

    const [displayTime, setDisplayTime] = useState(defaultTime);
    useEffect(() => {
      setDisplayTime(moment(time * 1000).format("YYYY-MM-DD[T]HH:mm:ss"));
    }, [time]);

    // comments associated with setting the connection
    const [comments, setComments] = useState("");

    // whether the panel is loading: usually happens after the "Replace" button
    // is clicked, waiting for a response from the DB.
    const [loading, setLoading] = useState(false);

    // set the time passed via props
    useEffect(() => {
        setTime(conn.start.time);
       console.log(conn)
    }, [])

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
                           Replace
                        </Typography>
                    </Grid>

                    <Grid item>
                        <CloseButton onClick={onClose} align="right" />
                    </Grid>
                </Grid>

                <Grid container spacing={2} justifyContent="center">

                    {/* <Grid item>
                        <TextField 
                            required
                            label="User" 
                            sx={{ width: 150 }}
                            // onChange={(event) => setUid(event.target.value)}
                        />
                    </Grid> */}

                    {/* // TODO: set time to prev */}
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
                        />
                    </Grid>

                </Grid>

                <ErrorMessage
                    style={{
                        marginTop: theme.spacing(1),
                    }}
                    errorMessage={errorMessage}
                />

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
                            uid === "" ||
                            time === defaultTime    
                        }
                        onClick={
                            async () => {
                                setLoading(true);
                                onSet( 
                                    time, 
                                    uid, 
                                    comments
                                ).then(
                                    successful => {
                                        if (successful === false) {
                                            setLoading(false);
                                            ;
                                        }
                                    }
                                )
                            }
                        }
                    >
                        {/**
                         * so when the panel is loading, the button
                         * is spinning.
                         */}
                        {(loading && !errorMessage) ? 
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

export default ComponentConnectionReplacePanel;
