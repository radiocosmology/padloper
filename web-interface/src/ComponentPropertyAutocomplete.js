import React, { useState, useEffect } from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';

export default function ComponentPropertyAutocomplete() {
    const [open, setOpen] = React.useState(false);
    const [options, setOptions] = React.useState([]);
    const loading = open && options.length === 0;

    useEffect(() => {
        
    }, [loading]);

    React.useEffect(() => {
        
    }, [open]);

    return (
        <Autocomplete
        id="property-autocomplete"
        sx={{ width: 300 }}
        open={open}
        onOpen={() => {
            setOpen(true);
        }}
        onClose={() => {
            setOpen(false);
        }}
        options={options}
        loading={loading}
        renderInput={(params) => (
            <TextField
            {...params}
            label="property-autocomplete-textfield"
            InputProps={{
                ...params.InputProps,
                endAdornment: (
                <React.Fragment>
                    {loading ? <CircularProgress color="inherit" size={20} /> : null}
                    {params.InputProps.endAdornment}
                </React.Fragment>
                ),
            }}
            />
        )}
        />
    );
    }