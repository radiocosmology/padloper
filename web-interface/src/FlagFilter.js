import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';

import Close from '@mui/icons-material/Close';

/**
 * 
 * @param {function} removeFilter - function to call when the filter is removed.
 * @param {function(int, object)} changeFilter - function to call when the 
 * filter is changed.
 * @param {int} index - the index of the filter 
 * (in an exterior list of filters).
 * @param {object} filter - the associated filter object (containing the name, flag type and flag severity)
 * @param {Array} type - the list of type to choose from (TODO: turn this 
 * @param {Array} severities - the list of severities to choose from (TODO: turn this 
 * into an autocomplete instead................)
 * @param {int} width - the width of the filter panel
 */
export default function FlagFilter(
        { 
            removeFilter, 
            changeFilter, 
            index, 
            filter, 
            type,
            severities,
            width
        }
    ) {

    /**
     * Update the filter with a new key/value pair.
     * @param {string} key - the key of the key/value pair 
     * @param {object} val - the new value
     */
    const filterUpdateKey = (key, val) => {
        let filterCopy = {...filter};
        filterCopy[key] = val;
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
     * Update the type key of the filter with the value from the select field.
     * @param {object} event - the event associated with the 
     * change of the TextField.
     */
    const filterUpdateType = (event) => {
        if (event.target.value != -1) {
            filterUpdateKey(
                'type', 
                type[event.target.value]['name']
            );
        }
        else {
            filterUpdateKey(
                'type', 
                ''
            );
        }
    }
    /**
     * Update the severity key of the filter with the value from the select field.
     * @param {object} event - the event associated with the 
     * change of the TextField.
     */
    const filterUpdateSeverity = (event) => {
        if (event.target.value != -1) {
            filterUpdateKey(
                'severity', 
                severities[event.target.value]['value']
            );
        }
        else {
            filterUpdateKey(
                'severity', 
                ''
            );
        }
    }

    // set the width of the filter's panel, set to 600px by default.
    let paperWidth = (width) ? width : '600px';

    // render the filter
    return (
        <Paper
            style={{
                marginTop: '8px',
                paddingTop: '8px',
                paddingBottom: '8px',
                width: paperWidth,
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
                <FormControl 
                    style={{
                        gridColumnStart: 2,
                    }}
                    variant="outlined"
                >
                    <Select
                        native
                        labelId={`flag-type-select-${index}-label`}
                        id={`flag-type-select-${index}`}
                        onChange={filterUpdateType}
                        displayEmpty
                    >
                        <option aria-label="None" value={-1} selected>
                            All types
                        </option>
                        {
                            type.map((t, index) =>
                                <option 
                                    value={index}
                                    key={index}
                                >
                                    {t['name']}
                                </option>
                            )
                        }
                    </Select>

                </FormControl>
                <FormControl 
                    style={{
                        gridColumnStart: 3,
                    }}
                    variant="outlined"
                >
                    <Select
                        native
                        labelId={`flag-severity-select-${index}-label`}
                        id={`flag-severity-select-${index}`}
                        onChange={filterUpdateSeverity}
                        displayEmpty
                    >
                        <option aria-label="None" value={-1} selected>
                            All Severities
                        </option>
                        {
                            severities.map((s, index) =>
                                <option 
                                    value={index}
                                    key={index}
                                >
                                    {s['value']}
                                </option>
                            )
                        }
                    </Select>

                </FormControl>

                <FormControl style={{
                        gridColumnStart: 4,
                    }}>
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
                </FormControl>


            </Stack>
        </Paper>
    )
}
