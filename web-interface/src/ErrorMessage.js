import React from 'react';
import Grid from '@mui/material/Grid';
import ErrorIcon from '@mui/icons-material/Error';
import { Typography } from '@mui/material';
import Stack from '@mui/material/Stack';

/**
 * Stylized component that represents any error messages that may be displayed.
 * 
 * @param {object} style - Specifies specific styles for error messages that may be
 *                          displayed in different contexts.
 * @param {string} errorMessage - The error message, if any, to be displayed.
 *                          If there is no error message to display, errorMessage is null. 
 */
export default function ErrorMessage({style, errorMessage}) {
    // Normalize various error payloads to a readable string
    const normalize = (err) => {
        if (err == null) return '';
        if (typeof err === 'string') {
            // Try to unwrap JSON-encoded strings (e.g., '"message"')
            try {
                const parsed = JSON.parse(err);
                return typeof parsed === 'string' ? parsed : JSON.stringify(parsed);
            } catch (_) {
                return err;
            }
        }
        if (err instanceof Error) return err.message || String(err);
        if (typeof err === 'object') {
            if (err.message) return String(err.message);
            try { return JSON.stringify(err); } catch (_) { return String(err); }
        }
        return String(err);
    };

    const msg = normalize(errorMessage);

    return (
        <>
            {msg ? (
                <Grid
                    container
                    direction="row"
                    style={style}
                    sx={{ paddingX: 2, justifyContent: 'center' }}
                >
                    <Stack direction="row" spacing={2}>
                        <ErrorIcon sx={{ color: 'red' }} />
                        <Typography style={{ color: 'rgb(255,0,0)' }}>
                            {msg}
                        </Typography>
                    </Stack>
                </Grid>
            ) : (
                <></>
            )}
        </>
    );
}
