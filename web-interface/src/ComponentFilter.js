import { 
    Paper, 
    TextField,
    Select,
    FormControl,
    Button,
    Stack
    } from '@mui/material';
import React, { useState } from 'react';
import './ComponentFilter.js';

import Close from '@mui/icons-material/Close';

/**
 * A MUI component that represents a filter object which allows to choose a
 * name for the component, a component type, and a revision. 
 * These are used in the ComponentList.
 * @param {function} removeFilter - function to call when the filter is removed.
 * @param {function(int, object)} changeFilter - function to call when the 
 * filter is changed.
 * @param {int} index - the index of the filter 
 * (in an exterior list of filters).
 * @param {object} - the associated filter object (containing the name and type)
 * @param {types} - the list of types and revisions to choose from 
 * (TODO: turn this into an autocomplete instead................)
 */
function ComponentFilter(
        {
            removeFilter, 
            changeFilter, 
            index, 
            filter, 
            types_and_revisions
        }
    ) {

    // the list of revisions for this specific element filter panel.
    const [revisions, setRevisions] = useState([]);

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
        if (event.target.value !== -1) {

            filterUpdateKey(
                'type', 
                types_and_revisions[event.target.value]['name']
            );

            setRevisions(types_and_revisions[event.target.value]['revisions'])
        }
        else {
            filterUpdateKey(
                'type', 
                ''
            );
            setRevisions([]);
        }
    }

     /**
     * Update the revision key of the filter with the 
     * value from the input field.
     * @param {object} event - the event associated with the 
     * change of the TextField.
     */
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
                        disabled={revisions.length === 0}
                    >
                        <option aria-label="None" value={""}>
                            {(revisions.length === 0) ? 
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

export default ComponentFilter;