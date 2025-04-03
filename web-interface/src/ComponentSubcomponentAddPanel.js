import React, { useState } from 'react';

import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import ErrorMessage from './ErrorMessage.js';
import CloseIcon from '@mui/icons-material/Close';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import styled from '@mui/material/styles/styled';
import { Typography } from '@mui/material';
import ComponentAutocomplete from './ComponentAutocomplete.js';
import ItemAutocomplete from './ItemAutocomplete.js';

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
 * The MUI component which represents a panel through which relation between two components where one is a subcomponent of another can be established.
 * 
 * @param {object} theme - A MUI theme object, see 
 * https://mui.com/material-ui/customization/theming/
 * @param {function} onClose - function to call when the close button is pressed
 * @param {function(string)} onSet - function to call when 
 * setting a component subcomponent connection. The parameters are of the form:
 * onSet(otherName), where otherName is the name of the
 * subcomponent you are connecting this one to.
 * @param {string} name - the name of the component you are connecting another
 * subcomponent to.
 */
function ComponentSubcomponentAddPanel(
    {
        theme,
        onClose,
        onSet,
        name,
        errorSubcomponentMessage
    }
) {

    // what the "selected" other component is
    const [selectedOption, setSelectedOption] = useState(null);

    // whether the panel is loading: usually happens after the "Set" button
    // is made, waiting for a response from the DB.
    const [loading, setLoading] = useState(false);

    function selectOption(option) {
        setSelectedOption(option);
    }

    const autocompleteQuery = '/api/component_list?range=0;100&orderBy=name&orderDirection=asc';
    // autocompleteQuery += `?range=0;100`; // get the first 100, don't want too much
    // autocompleteQuery += `&orderBy=name`
    // autocompleteQuery += `&orderDirection=asc`;

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
                            Connect a subcomponent
                        </Typography>
                    </Grid>

                    <Grid item>
                        <CloseButton onClick={onClose} align="right" />
                    </Grid>
                </Grid>

                <Grid container spacing={2} justifyContent="space-around">
                    <Grid item>
                        <ItemAutocomplete 
                            onSelect={selectOption} 
                            excludeName={name}
                            queryString={autocompleteQuery}
                            label={"Component"}
                        />
                    </Grid>

                </Grid>

                <ErrorMessage
                    style={{
                        marginTop: theme.spacing(1),
                    }}
                    errorMessage={errorSubcomponentMessage}
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
                            selectedOption === null  
                        }
                        onClick={
                            async () => {
                                setLoading(true);
                                onSet(
                                    selectedOption.name,
                                )
                            }
                        }
                    >
                        {/**
                         * so when the panel is loading, the button
                         * is spinning.
                         */}
                        {(loading && !errorSubcomponentMessage)
                         ? 
                        errorSubcomponentMessage ?
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

export default ComponentSubcomponentAddPanel;