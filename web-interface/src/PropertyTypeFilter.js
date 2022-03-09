import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import FormControl from '@mui/material/FormControl';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';

import Close from '@mui/icons-material/Close';

export default function PropertyTypeFilter(
        { 
            removeFilter, 
            changeFilter, 
            index, 
            filter, 
            types,
            width
        }
    ) {

    // update a specific value of the filter by key
    const filterUpdateKey = (key, val) => {
        let filterCopy = {...filter};
        filterCopy[key] = val;
        changeFilter(index, filterCopy);
    }

    // update the name key of the filter with the value from the input field.
    const filterUpdateName = (event) => {
        filterUpdateKey('name', event.target.value);
    }

    // update the type key of the filter with the value from the select field.
    const filterUpdateType = (event) => {
        if (event.target.value != -1) {
            filterUpdateKey(
                'type', 
                types[event.target.value]['name']
            );
        }
        else {
            filterUpdateKey(
                'type', 
                ''
            );
        }
    }

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
                        labelId={`component-type-select-${index}-label`}
                        id={`component-type-select-${index}`}
                        onChange={filterUpdateType}
                        displayEmpty
                    >
                        <option aria-label="None" value={-1} selected>
                            All types
                        </option>
                        {
                            types.map((t, index) =>
                                <option 
                                    value={index}
                                >
                                    {t['name']}
                                </option>
                            )
                        }
                    </Select>

                </FormControl>

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