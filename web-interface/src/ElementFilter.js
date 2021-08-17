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

function ElementFilter(
        { addFilter, 
            removeFilter, 
            changeFilter, 
            index, 
            filter, 
            types_and_revisions
        }
    ) {
    
    const classes = useStyles();

    const [revisions, setRevisions] = useState([]);

    const filterUpdateKey = (key, val) => {
        let filterCopy = {...filter};
        filterCopy[key] = val;
        changeFilter(index, filterCopy);
    }

    const filterUpdateName = (event) => {
        filterUpdateKey('name', event.target.value);
    }

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

    const filterUpdateRevision = (event) => {
        filterUpdateKey('revision', event.target.value);
    }

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
                className={classes.rev_select_form_control}
                variant="outlined"
            >
                <Select
                    native
                    labelId={`component-revision-select-${index}-label`}
                    id={`component-revision-select-${index}`}
                    onChange={filterUpdateRevision}
                    className={classes.select}
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
                className={classes.close_button}
                onClick={() => removeFilter(index)}
            >
                <Close />
            </Button>
            
        </Paper>
    )
}

export default ElementFilter;