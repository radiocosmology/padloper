import React, { useState, useEffect } from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';

/**
 * An Autocomplete component that queries the component list in the DB and gives
 * a text field with possible values to select in the dropdown.
 * 
 * @param {function(string)} onSelect - function to call when value is selected.
 * @param {string} excludeName - what name, if any, to select from the dropdown.
 */
    
export default function ComponentAutocomplete(
    {
        onSelect,
        excludeName,
    }
) {
    // note that the "excludeName" attribute should be an ignored name when
    // listing the components.

    // whether the autocomplete is open
    const [open, setOpen] = useState(false);

    // list of options to pick from
    const [options, setOptions] = useState([]);
    
    // what is contained inside the text field
    const [entered_string, setEnteredString] = useState(""); 

    // whether the list of options is currently loading the list of components
    const [loading, setLoading] = useState(open && options.length === 0);

    useEffect(() => {

        async function fetchData() {
            setLoading(true);

            // create the URL query string
            let input = '/api/component_list';
            input += `?range=0;100`; // get the first 100, don't want too much
            input += `&orderBy=name`
            input += `&orderDirection=asc`;
            input += `&filters=${entered_string},,`; // double comma needed
    
            // query the URL with flask, and set the input.
            fetch(input).then(
                res => res.json()
            ).then(data => {
                // get rid of the element with the same name 
                // as "excludeName" parameter
                let index = data.result.findIndex(
                    (option) => option.name === excludeName
                );
                if (index > -1) {
                    data.result.splice(index, 1);
                }
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

    /**
     * basically copied from 
     * https://mui.com/components/autocomplete/#asynchronous-requests
     */
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
