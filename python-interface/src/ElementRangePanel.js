import React, { useState, useEffect } from 'react';
import { Paper, Button, Box, Select, MenuItem, FormHelperText } 
    from '@material-ui/core';

import { makeStyles } from '@material-ui/core/styles';

import { ArrowForward, ArrowBack } from '@material-ui/icons';



const useStyles = makeStyles((theme) => ({
    root: {
        marginTop: theme.spacing(1),
        padding: theme.spacing(1),
        flexGrow: 1,
        marginBottom: theme.spacing(1),
        textAlign: 'center',
        display: 'grid',
        rowGap: theme.spacing(0.5),
    },
    num_display: {
        gridColumnStart: 1,
        gridColumnEnd: 2,
    },
    range_select: {
        marginRight: theme.spacing(1),
        marginLeft: theme.spacing(1),
    },
    change_range_button: {
        marginRight: theme.spacing(1),
        marginLeft: theme.spacing(1),
    }
}));

function ElementRangePanel({ min, updateMin, range, updateRange, count }) {

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

    const classes = useStyles();

    let max = min + range;
    if (max >= count) {
        max = count;
    }

    return (
        <Paper className={classes.root}>
            <Box component="span" className={classes.num_display}>
                Viewing {min+1}-{max} components out of {count}
            </Box>
            <Box component="span">
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

                View 
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
                components at a time

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
            </Box>
        </Paper>
    )
}

export default ElementRangePanel;