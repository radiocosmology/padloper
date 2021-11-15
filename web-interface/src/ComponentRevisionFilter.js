import { 
    Paper, 
    TextField,
    Select,
    FormControl,
    InputLabel,
    Button
    } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import React, { useState, useEffect } from 'react';

import { Close } from '@material-ui/icons';

// styling for the React elements 
const useStyles = makeStyles((theme) => ({
    root: {
        marginTop: theme.spacing(1),
        paddingTop: theme.spacing(1),
        paddingBottom: theme.spacing(1),
        width: theme.spacing(75),
        maxWidth: '100%',
        marginLeft: 'auto',
        marginRight: 'auto',
        textAlign: 'center',
        display: 'grid',
        alignItems: 'stretch',
    },
    text_field: {
        marginLeft: theme.spacing(2),
        gridColumnStart: 1,
    },
    type_select_form_control: {
        marginLeft: theme.spacing(2),
        minWidth: 140,
        gridColumnStart: 2,
    },
    rev_select_form_control: {
        marginLeft: theme.spacing(2),
        minWidth: 140,
        gridColumnStart: 3,
    },
    select: {
    },
    close_button: {
        marginTop: 'auto',
        marginBottom: 'auto',
        gridColumnStart: 4,
        marginLeft: theme.spacing(2),
        marginRight: theme.spacing(2),
        height: '100%',
    }

}));

function ComponentRevisionFilter(
        { 
            removeFilter, 
            changeFilter, 
            index, 
            filter, 
            types
        }
    ) {
    
    const classes = useStyles();

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
                types[event.target.value]['name']
            );
        }
        else {
            filterUpdateKey(
                'component_type', 
                ''
            );
        }
    }

    // render the filter
    return (
        <Paper className={classes.root}>
            <TextField 
                label="Filter by name" 
                variant="outlined" 
                className={classes.text_field}
                onChange={filterUpdateName}
            />
            <FormControl 
                className={classes.type_select_form_control}
                variant="outlined"
            >
                <Select
                    native
                    labelId={`component-type-select-${index}-label`}
                    id={`component-type-select-${index}`}
                    onChange={filterUpdateType}
                    className={classes.select}
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
                className={classes.close_button}
                onClick={() => removeFilter(index)}
            >
                <Close />
            </Button>
            
        </Paper>
    )
}

export default ComponentRevisionFilter;