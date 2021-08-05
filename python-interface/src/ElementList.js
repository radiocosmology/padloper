import React, { useState, useEffect } from 'react';
import { Paper, Box, Table, TableBody, TableRow, 
    TableHead, TableCell, TableContainer, 
    CircularProgress } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    root: {
        marginTop: theme.spacing(1),
        textAlign: 'center',
    },
    progress: {
        paddingTop: theme.spacing(2),
        paddingBottom: theme.spacing(2),
    }
}));

function createData(name, id) {
    return { name, id };
}  



function ElementList({ components, loaded }) {
    
    const classes = useStyles();

    let rows = components.map((c) => createData(c.name, c.id))

    let content = <CircularProgress className={classes.progress} />;

    if (loaded) {
        content = (
        <TableContainer component={Paper} className={classes.root}>
            <Table className={classes.table} aria-label="simple table">
                <TableHead>
                <TableRow>
                    <TableCell>Component Name</TableCell>
                    <TableCell align="right">ID</TableCell>
                </TableRow>
                </TableHead>
                <TableBody>
                {rows.map((row) => (
                    <TableRow key={row.name}>
                    <TableCell component="th" scope="row">
                        {row.name}
                    </TableCell>
                    <TableCell align="right">{row.id}</TableCell>
                    </TableRow>
                ))}
                </TableBody>
            </Table>
        </TableContainer>
        )
    }

    return (
        <Paper className={classes.root}>
            {content}
        </Paper>
        
    )
}

export default ElementList;
