import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { 
    Paper, 
} from '@material-ui/core';

import {
    useParams
} from "react-router-dom";

// styling for the React elements 
const useStyles = makeStyles((theme) => ({
    root: {
        marginTop: theme.spacing(1),
        paddingTop: theme.spacing(1),
        paddingBottom: theme.spacing(1),
        width: theme.spacing(100),
        maxWidth: '100%',
        marginLeft: 'auto',
        marginRight: 'auto',
        textAlign: 'center',
    },
}));

function ComponentPage() {

    const classes = useStyles();

    let { name } = useParams();

    // the list of components in objects representation
    const [component, setComponent] = useState(undefined);

    useEffect(() => {
        fetch(`/api/components_name/${name}`).then(
            res => res.json()
        ).then(data => {
            console.log(data.result);
            setComponent(data.result);
        });
    }, []);

    let content = (
        <>
            Loading...
        </>
    )

    if (component) {
        content = (
            <>
                <h3>
                    {component.name}
                </h3>
                <h4>
                    {component.type.name}
                </h4>
            </>
        )
    }

    return (
        <Paper className={classes.root}>
            {content}
        </Paper>
    )
}

export default ComponentPage;