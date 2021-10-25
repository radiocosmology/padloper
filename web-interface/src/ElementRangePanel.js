import React, { useState, useEffect } from 'react';
import { 
    Paper, 
    Button, 
    Box, 
    Select, 
    MenuItem, 
    Divider } 
    from '@material-ui/core';

import { makeStyles } from '@material-ui/core/styles';

import { ArrowForward, ArrowBack, Autorenew } from '@material-ui/icons';


// styling for the React elements
const useStyles = makeStyles((theme) => ({
    root: {
        marginTop: theme.spacing(2),
        paddingTop: theme.spacing(1),
        paddingBottom: theme.spacing(1),
        flexGrow: 1,
        marginBottom: theme.spacing(1),
        textAlign: 'center',
        display: 'grid',
        justifyContent: 'space-between',
        rowGap: theme.spacing(1),
        width: theme.spacing(75),
        maxWidth: '100%',
        margin: 'auto',
    },
    num_display_wrapper: {
        gridRow: '1',
        gridColumn: '1',
        margin: 'auto',
        paddingTop: theme.spacing(1),
    },
    range_select: {
        marginRight: theme.spacing(1),
        marginLeft: theme.spacing(1),
    },
    change_range_button: {
        marginRight: theme.spacing(1),
        marginLeft: theme.spacing(1),
        padding: theme.spacing(2),
    },
    range_wrapper: {
        gridRow: '2',
        gridColumn: '1 / 2',
        margin: 'auto',
    },
    right_column_wrapper: {
        gridRow: '1 / 3',
        gridColumn: '2',
        marginLeft: theme.spacing(2),
        marginRight: theme.spacing(2),
        marginTop: 'auto',
        marginBottom: 'auto',
    },
    
}));

function ElementRangePanel(
        { 
            min, 
            updateMin, 
            range, 
            updateRange, 
            count, 
            rightColumn,
        }
    ) {

    const classes = useStyles();

    // function to call when the component range is changed. is changed.
    const handleRangeChange = (event) => {
        updateRange(event.target.value);
    }

    const changeMin = (min, updateMin, range, count, increment) => {
        /*
        Increment the range minimum of components to view.
        */
    
        let newMin = min;
    
        if (increment) {
            if (newMin + range < count) {
                newMin += range;
            }
        }
        else {
            if (newMin < range) {
                newMin = 0;
            }
            else {
                newMin -= range;
            }
        }
    
        updateMin(newMin);
    }

    let max = min + range;
    if (max >= count) {
        max = count;
    }

    let numDisplayText = `Viewing ${min+1}-${max} out of ${count}`
    if (count == 0) {
        numDisplayText = "No objects found";
    }

    // return the range panel.
    return (
        <Paper className={classes.root}>
            <div component="span" className={classes.num_display_wrapper}>
                {numDisplayText}
            </div>
            <div className={classes.range_wrapper}>
                <Button 
                    color="primary" 
                    className={classes.change_range_button}
                    onClick={() => {
                        changeMin(min, updateMin, range, count, false)
                    }}
                    disabled={min <= 0}
                >
                    <ArrowBack />
                </Button>

                Show 
                <Select
                    labelId="range-select-label"
                    id="range-select"
                    value={range}
                    onChange={handleRangeChange}
                    className={classes.range_select}
                    displayEmpty 
                >
                    <MenuItem value={10}>10</MenuItem>
                    <MenuItem value={25}>25</MenuItem>
                    <MenuItem value={50}>50</MenuItem>
                    <MenuItem value={100}>100</MenuItem>
                </Select>
                at a time

                <Button 
                    color="primary" 
                    className={classes.change_range_button}
                    onClick={() => {
                        changeMin(min, updateMin, range, count, true)
                    }}
                    disabled={max >= count}
                >
                    <ArrowForward />
                </Button>
            </div>

            <div className={classes.right_column_wrapper}>
                {rightColumn}
            </div>
        </Paper>
    )
}

export default ElementRangePanel;