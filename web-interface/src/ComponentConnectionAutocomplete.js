import React, { useState, useEffect } from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';

export default function ComponentConnectionAutocomplete(
    {
        onSelect,
    }
) {
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
            let input = '/api/component_list';
            input += `?range=0;100`;
            input += `&orderBy=name`
            input += `&orderDirection=asc`;
            input += `&filters=${entered_string},,`; // double comma needed
    
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
        id="component-autocomplete"
        sx={{ width: 200 }}
        open={open}
        onOpen={() => {
            setOpen(true);
        }}
        onClose={() => {
            setOpen(false);
        }}
        options={options}
        isOptionEqualToValue={(option, value) => option.name === value.name}
        getOptionLabel={(option) => option.name}
        onInputChange={(option, value, details) => setEnteredString(value)}
        onChange={(event, value, reason, details) => onSelect(value)}
        loading={loading}
        renderInput={(params) => (
            <TextField  
            variant="filled"
            {...params}
            label="Component"
            InputProps={{
                ...params.InputProps,
                endAdornment: (
                <React.Fragment>
                    {loading 
                        ? <CircularProgress color="inherit" size={20} /> 
                        : null
                    }
                    {params.InputProps.endAdornment}
                </React.Fragment>
                ),
            }}
            />
        )}
        />
    );
    }