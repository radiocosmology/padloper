import React from 'react';
import Grid from '@mui/material/Grid';
import ErrorIcon from '@mui/icons-material/Error';
import { Typography } from '@mui/material';

/**
 * Represents any error messages that may be displayed.
 * 
 * @param {object} style - Specifies specific styles for error messages that may 
 *                          displayed in different contexts.
 * @param {string} errorMessage - The error message, if any, to be displayed.
 *                          If there is no error message to display, errorMessage is null. 
 */
export default function ErrorMessage({style, errorMessage}) {

    return (
        <>
            {
                errorMessage
                    ?
                    <Grid
                        container
                        style={style}
                        spacing={1}
                        justifyContent="center"
                        sx={{paddingX: 2}}
                    >
                        <Grid item>
                            <ErrorIcon sx={{ color: 'red' }} />
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
                    </Grid>
                    :
                    <></>
            }
        </>

    )
}