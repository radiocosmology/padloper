import { 
    Paper, 
    TextField,
    Select,
    FormControl,
    InputLabel,
    Button,
    Stack
    } from '@mui/material';
import { styled } from '@mui/material/styles';
import React, { useState, useEffect } from 'react';
import './ElementFilter.js';

import Close from '@mui/icons-material/Close';

function ElementFilter(
        { addFilter, 
            removeFilter, 
            changeFilter, 
            index, 
            filter, 
            types_and_revisions
        }
    ) {

    // the list of revisions for this specific element filter panel.
    const [revisions, setRevisions] = useState([]);

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
                'component_type', 
                types_and_revisions[event.target.value]['name']
            );

            setRevisions(types_and_revisions[event.target.value]['revisions'])
        }
        else {
            filterUpdateKey(
                'component_type', 
                ''
            );
            setRevisions([]);
        }
    }

    // update the revision key of the filter with the 
    // value from the select field.
    const filterUpdateRevision = (event) => {
        filterUpdateKey('revision', event.target.value);
    }

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
                display: 'grid',
                alignItems: 'stretch',
            }}
        >
            <Stack direction="row" spacing={2}>
                <TextField 
                    label="Filter by name" 
                    variant="outlined" 
                    style={{
                        gridColumnStart: 1,
                        marginLeft: '16px',
                    }}
                    onChange={filterUpdateName}
                />
                <FormControl 
                    className="SelectDropdown"
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
                            types_and_revisions.map((t, index) =>
                                <option 
                                    value={index}
                                >
                                    {t['name']}
                                </option>
                            )
                        }
                    </Select>

                </FormControl>

                <FormControl
                    className="SelectDropdown" 
                    style={{
                        gridColumnStart: 3,
                    }}
                    variant="outlined"
                >
                    <Select
                        native
                        labelId={`component-revision-select-${index}-label`}
                        id={`component-revision-select-${index}`}
                        onChange={filterUpdateRevision}
                        disabled={revisions.length == 0}
                    >
                        <option aria-label="None" value={""}>
                            {(revisions.length == 0) ? 
                                "Select a type" 
                                : "All revisions"
                            }
                        </option>
                        {
                            revisions.map((name) =>
                                <option value={name}>{name}</option>
                            )
                        }
                    </Select>

                </FormControl>

                <Button 
                    color="primary" 
                    style={{
                        marginTop: 'auto',
                        marginBottom: 'auto',
                        gridColumnStart: 4,
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

export default ElementFilter;