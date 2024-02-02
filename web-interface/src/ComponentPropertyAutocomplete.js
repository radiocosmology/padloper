import React, { useState, useEffect } from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';

/**
 * An Autocomplete component that queries the component property list in the DB 
 * and gives a text field with possible values to select in the dropdown.
 * 
 * @param {function(string)} onSelect - function to call when value is selected.
 */
export default function ComponentPropertyAutocomplete(
    {
        onSelect,
        selected
    }
) {

    // whether the autocomplete is open
    const [open, setOpen] = useState(false);

    // list of options to pick from
    const [options, setOptions] = useState([]);
    
    // what is contained inside the text field
    const [entered_string, setEnteredString] = useState(""); 

    // whether the list of options is currently loading the list of components
    const [loading, setLoading] = useState(open && options.length === 0);

    const [selectedOption, setSelectedOption] = useState({});

    useEffect(() => {
        // setEnteredString(selected ? selected : "");
        if (selected) {
            setSelectedOption(selected);
            onSelect(selected);
        }
        console.log(selectedOption);
    }, [])

    /**
     * When the entered string is changed or the autocomplete has been opened,
     * query the list.
     */
    useEffect(() => {
        async function fetchData() {
            setLoading(true);

            // create the URL query string
            let input = '/api/property_type_list';
            input += `?range=0;100`;
            input += `&orderBy=name`
            input += `&orderDirection=asc`;
            input += `&nameSubstring=${entered_string}`;
    
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

    /**
     * basically copied from 
     * https://mui.com/components/autocomplete/#asynchronous-requests
     */
    return (
        <Autocomplete
        id="property-autocomplete"
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
        getOptionLabel={(option) =>  option && option.name ? option.name : ''}
        onInputChange={(option, value, details) => {
            setEnteredString(value);
            if (option && option.name) {
                setSelectedOption(option)
            }
        }}
        onChange={(event, value, reason, details) => onSelect(value)}
        value={selectedOption}
        loading={loading}
        renderInput={(params) => (
            <TextField  
            variant="filled"
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
