import React, { useState, useEffect } from 'react';
import { Paper, Box, Table, TableBody, TableRow, TableHead, TableCell, TableContainer } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    root: {
        marginTop: theme.spacing(1),
    },
}));

function createData(name, id) {
    return { name, id};
}  



function ElementList({ components }) {
    
    const classes = useStyles();

    let rows = components.map((c) => createData(c.name, c.id))

    return (
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

export default ElementList;
