import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

import CloseIcon from '@mui/icons-material/Close';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';

const Panel = styled((props) => (
    <Paper 
        elevation={0}
        {...props}
        sx={{margin:-1}}
    />
))(({ theme }) => ({
    backgroundColor: 'rgb(225, 225, 255)',
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


function ComponentEventAddPanel(
    {
        theme,
        onClose
    }
) {
    return (
        <ThemeProvider theme={theme}>
            <Panel>

                <Box style={{textAlign: 'right'}}>
                    <CloseButton onClick={onClose} />
                </Box>

                Add stuff here.

                <Box 
                    style={{
                        textAlign: 'right',
                    }}
                >
                    <Button variant="contained">Add</Button>
                </Box>
            </Panel>
        </ThemeProvider>
    )
}

export default ComponentEventAddPanel;