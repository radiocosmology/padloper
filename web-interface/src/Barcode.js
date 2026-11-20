import React, { useState, useEffect } from 'react';

import { styled } from '@mui/material/styles';
import { Paper, Typography, Grid, Stack, Box, Button } from '@mui/material';

import Authenticator from './components/Authenticator';


const Item = styled(Paper)(({ theme }) => ({
    backgroundColor: '#fff',
    ...theme.typography.body2,
    padding: theme.spacing(1),
    textAlign: 'center',
    color: (theme.vars ?? theme).palette.text.secondary,
    ...theme.applyStyles('dark', {
        backgroundColor: '#1A2027',
    }),
}))

function Barcode() {
    /**
     * Handle a scanned barcode when 'barcodescan' event triggered.
     */
    const handleBarcode = (e) => {
        let barcode = e.detail.barcode;
        console.log(barcode);
    }

    /**
     * Detect barcode scanning and trigger the 'barcodescan' event.
     *
     * Scanning a barcode emulates typing characters extremely fast, so
     * this listens for keypress events and checks if they happen fast
     * enough to be likely from scanning a barcode.
     */
    useEffect(() => {
        var timeoutHandler = 0;
        var inputString = '';
        const detectBarcode = (event) => {
            if (timeoutHandler) {
                clearTimeout(timeoutHandler);
            }
            inputString += event.key;

            timeoutHandler = setTimeout(() => {
                if (inputString.length <= 3) {
                    inputString = '';
                } else {
                    let barcodeEvent = new CustomEvent(
                        "barcodescan", { detail: { barcode: inputString } }
                    );
                    window.dispatchEvent(barcodeEvent);
                    inputString = '';
                }
            }, 50);
        }
        window.addEventListener('keypress', detectBarcode);
        window.addEventListener('barcodescan', handleBarcode);

        return () => {
            window.removeEventListener('keypress', detectBarcode);
            window.removeEventListener('barcodescan', handleBarcode);
        }
    }, []);

    return (
        <>
            <Authenticator />
            <Paper
                sx={{
                    mt: 4,
                    p: 4,
                    mb: 2,
                    margin: 'auto',
                    width: '100%',
                    maxWidth: {
                        md: '600px',
                    },
                }}
            >
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <Typography
                            component="h1"
                            variant="h5"
                            sx={{ textAlign: 'center' }}
                        >
                            Barcode Scanner
                        </Typography>
                    </Grid>
                    <Grid item xs={4}>
                        <Button fullWidth variant="contained">Find Component</Button>
                    </Grid>
                    <Grid item xs={4}>
                        <Button fullWidth variant="contained">Add Component</Button>
                    </Grid>
                    <Grid item xs={4}>
                        <Button fullWidth variant="contained">Replace Component</Button>
                    </Grid>
                </Grid>
            </Paper>
        </>
    )
}

export default Barcode;
