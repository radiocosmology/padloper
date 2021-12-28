import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';

import CloseIcon from '@mui/icons-material/Close';

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
    return (
        <ThemeProvider theme={theme}>
            <Panel>

                <Grid container spacing={2} justifyContent="space-between">
                    <Grid item>Set a property</Grid>

                    <Grid item>
                        <CloseButton onClick={onClose} align="right" />
                    </Grid>
                </Grid>

                <Grid container spacing={2} justifyContent="space-around">
                    <Grid item>
                        <ComponentPropertyAutocomplete />
                    </Grid>

                    <Grid item>
                        <TextField 
                            label="User" 
                            variant="outlined" 
                        />
                    </Grid>

                    <Grid item>
                    <TextField
                        id="datetime-local"
                        label="Time"
                        type="datetime-local"
                        sx={{ width: 250 }}
                        InputLabelProps={{
                            shrink: true,
                        }}
                    />
                    </Grid>
                </Grid>

                <TextField
                    id="outlined-multiline-static"
                    label="Comments"
                    multiline
                    rows={2}
                />

                <Box 
                    style={{
                        textAlign: 'right',
                        marginTop: theme.spacing(2),
                    }}
                >
                    <Button variant="contained">Add</Button>
                </Box>
            </Panel>
        </ThemeProvider>
    )
}

export default ComponentPropertyAddPanel;