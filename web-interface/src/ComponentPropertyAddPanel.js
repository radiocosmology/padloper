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
                            onSelect={setSelectedOption} 
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

                <Grid>

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