import React, { useState, useEffect } from 'react';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import MuiTextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';

import CloseIcon from '@mui/icons-material/Close';
import ErrorIcon from '@mui/icons-material/Error';
import PersonIcon from '@mui/icons-material/Person';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';
import { Typography } from '@mui/material';
import { verifyRegex } from './utility/utility.js';
import { SettingsSuggestRounded } from '@mui/icons-material';
import ComponentConnectionAutocomplete from './ComponentConnectionAutocomplete.js';

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


function ComponentConnectionAddPanel(
    {
        theme,
        onClose,
        onSet,
        name
    }
) {

    const [selectedOption, setSelectedOption] = useState(null);

    const [uid, setUid] = useState("");

    const defaultTime = 1;

    const [time, setTime] = useState(defaultTime);

    const [comments, setComments] = useState("");

    const [loading, setLoading] = useState(false);

    const [errorMessage, setErrorMessage] = useState("");

    function regexCheck(value) {
        if (!selectedOption) {
            return false;
        }
        return verifyRegex(value, selectedOption.allowed_regex);
    }

    function selectOption(option) {
        setSelectedOption(option);
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
                            Connect a component
                        </Typography>
                    </Grid>

                    <Grid item>
                        <CloseButton onClick={onClose} align="right" />
                    </Grid>
                </Grid>

                <Grid container spacing={2} justifyContent="space-around">
                    <Grid item>
                        <ComponentConnectionAutocomplete 
                            onSelect={selectOption} 
                            name={name}
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

                {errorMessage !== "" ? 
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
                                {errorMessage}
                            </Typography>
                        </Grid>
                    </Grid> : <></>
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
                            () => {
                                setErrorMessage("");
                                setLoading(true);
                                onSet(
                                    selectedOption.name, 
                                    time, 
                                    uid, 
                                    comments
                                ).then(
                                    successful => {
                                        if (!successful) {
                                            setLoading(false);
                                            setErrorMessage(`This component is 
                                            already connected to 
                                            ${selectedOption.name}.`);
                                        }
                                    }
                                )
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

export default ComponentConnectionAddPanel;