import React, { useState, useEffect } from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';

export default function ComponentPropertyAutocomplete() {
    const [open, setOpen] = useState(false);
    const [options, setOptions] = useState([]);
    
    // what is contained inside the text field
    const [entered_string, setEnteredString] = useState(""); 

    const [loading, setLoading] = useState(open && options.length === 0);

    useEffect(() => {
        
    }, [open]);

    useEffect(() => {

        async function fetchData() {
            setLoading(true);

            // create the URL query string
            let input = '/api/property_type_list';
            input += `?range=0;100`;
            input += `&orderBy=name`
            input += `&orderDirection=asc`;
            input += `&filters=${entered_string}`;
    
            // query the URL with flask, and set the input.
            fetch(input).then(
                res => res.json()
            ).then(data => {
                setOptions(data.result);
    
                setLoading(false);
            });
        }
        if (open) {
            fetchData();
        }
        else {
            setLoading(false);
        }
    }, [entered_string, open]);

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
        getOptionLabel={(option) => option.name}
        loading={loading}
        renderInput={(params) => (
            <TextField
            {...params}
            label="Property Type"
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