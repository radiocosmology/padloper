import React, { useState, useEffect } from 'react';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import ThemeProvider from '@mui/material/styles/ThemeProvider';
import createTheme from '@mui/material/styles/createTheme';
import styled from '@mui/material/styles/styled';
import './ComponentPage.css';

import {
    useParams
} from "react-router-dom";

const ComponentNameWrapper = styled(Paper)(({ theme }) => ({
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.common.white,
    margin: 'auto',
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
    width: '300px',
    height: '200px',
    fontSize: '300%',
    lineHeight: '200px',
}));

const theme = createTheme();

function ComponentPage() {
    let { name } = useParams();

    // the list of components in objects representation
    const [component, setComponent] = useState(undefined);

    useEffect(() => {
        fetch(`/api/components_name/${name}`).then(
            res => res.json()
        ).then(data => {
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
            <ThemeProvider theme={theme}>
                <Stack direction="row" spacing={2}>
                    <ComponentNameWrapper>
                        {component.name}
                    </ComponentNameWrapper>
                    <div>
                        <h2>
                            {component.type.name}
                        </h2>
                        <h2>
                            {component.revision.name}
                        </h2>
                    </div>
                </Stack>

                PUT STUFF HERE

            </ThemeProvider>
        )
    }

    return (
        <Paper className="Root">
            {content}
        </Paper>
    )
}

export default ComponentPage;