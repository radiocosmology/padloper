import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import ItemAutocomplete from './ItemAutocomplete.js'
import Close from '@mui/icons-material/Close';
import { useEffect, useState } from 'react';

/**
 * A MUI component that represents a filter object which allows to choose a
 * name for the version along with an associated type. These are used in the
 * ComponentVersionList.
 * @param {function} removeFilter - function to call when the filter is removed.
 * @param {function(int, object)} changeFilter - function to call when the 
 * filter is changed.
 * @param {int} index - the index of the filter 
 * (in an exterior list of filters).
 * @param {object} filter - the associated filter object (containing the name 
 * and type)
 * @param {Array} types - the list of types to choose from (TODO: turn this 
 * into an autocomplete instead................)
 */
function ComponentVersionFilter(
        { 
            removeFilter, 
            changeFilter, 
            index, 
            filter, 
            types
        }
    ) {

    const [selectedType, setSelectedType] = useState('');

    // query string to be used in component type autocomplete
    const typeQuery = '/api/component_type_list?range=0;-1&' + 
    'orderBy=name&orderDirection=asc&nameSubstring=';

    /**
     * Update the filter with a new key/value pair.
     * @param {string} key - the key of the key/value pair 
     * @param {object} val - the new value
     */
    const filterUpdateKey = (key, val) => {

        // do a copy of the object
        let filterCopy = {...filter};

        // set the key/value pair
        filterCopy[key] = val;

        // update it
        changeFilter(index, filterCopy);
    }

    /**
     * Update the name key of the filter with the value from the input field.
     * @param {object} event - the event associated with the 
     * change of the TextField.
     */
    const filterUpdateName = (event) => {
        filterUpdateKey('name', event.target.value);
    }

    /**
     * Update the filters when the selected type is updated
     */
    useEffect (() => {
        if (selectedType) {
            filterUpdateKey('type', selectedType.name);
        }
        else {      // selectedType is empty
            filterUpdateKey('type', '');
        }
    }, [selectedType])

    // render the filter
    return (
        <Paper
            style={{
                marginTop: '8px',
                paddingTop: '8px',
                paddingBottom: '8px',
                width: '600px',
                maxWidth: '100%',
                marginLeft: 'auto',
                marginRight: 'auto',
                textAlign: 'center',
            }}
        >
            <Stack direction="row" spacing={2}
                style={{
                    display: 'grid',
                    alignItems: 'stretch',
                }}
            >
            
                <TextField 
                    label="Filter by name" 
                    variant="outlined" 
                    style={{
                        marginLeft: "16px",
                        gridColumnStart: 1,
                    }}
                    onChange={filterUpdateName}
                />
                <ItemAutocomplete
                    onSelect={(type) => {setSelectedType(type)}}
                    queryString={typeQuery}
                    label={"Component Type"}
                />
                <Button 
                    color="primary" 
                    style={{
                        marginTop: 'auto',
                        marginBottom: 'auto',
                        gridColumnStart: 3,
                        marginLeft: '16px',
                        marginRight: '16px',
                        height: '100%',
                    }}
                    onClick={() => removeFilter(index)}
                >
                    <Close />
                </Button>

            </Stack>
        </Paper>
    )
}

export default ComponentVersionFilter;
