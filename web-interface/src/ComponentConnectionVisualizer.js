import React from 'react';
import ReactFlow, { Controls, Background } from 'react-flow-renderer';
import styled from '@mui/material/styles/styled';
import createTheme from '@mui/material/styles/createTheme';
import { Link } from "react-router-dom";

import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';

import UnfoldMoreIcon from '@mui/icons-material/UnfoldMore';

import ComponentAutocomplete from './ComponentAutocomplete.js';
import { ThemeProvider } from '@emotion/react';

const theme = createTheme({
    typography: {
        body2: {
            fontWeight: 800,
            fontSize: 16,
        },
    }
});

const TextLink = styled((props) => (
    <Link
        {...props}
        style={{
            textDecoration: 'none',    
        }}
    />
))(({ theme }) => ({
}));

const Root = styled((props) => (
    <Paper 
        {...props}
    />
))(({ theme }) => ({
    marginTop: theme.spacing(1),
    padding: theme.spacing(1),
    width: '1200px',
    maxWidth: '100%',
    marginLeft: 'auto',
    marginRight: 'auto',
    textAlign: 'center',
}));

const OptionsPanel = styled((props) => (
    <Paper 
        {...props}
    />
))(({ theme }) => ({
    width: '1000px',
    maxWidth: '100%',
    textAlign: 'center',
    marginTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
}));

const VisualizerPanel = styled((props) => (
    <Paper 
        elevation={2}
        {...props}
    />
))(({ theme }) => ({
    height: '540px',
    width: '1000px',
    maxWidth: '100%',
}));

const ExpandConnectionsButton = styled((props) => (
    <Button 
        style={{
            maxWidth: '30px',
            minWidth: '30px',
            maxHeight: '30px',
            minHeight: '30px',
        }}
        {...props}
    >
        <UnfoldMoreIcon />
    </Button>
))(({ theme }) => ({
}));


function ComponentNode({name}) {
    return (
        <ThemeProvider theme={theme}>
            <Grid 
                container
                justifyContent="center"
                alignItems="center"
            >
                <Grid item xs={9}>
                    <Typography
                        variant="body2"
                    >
                        <TextLink to={`/component/${name}`}>
                            {name}
                        </TextLink>
                    </Typography>
                </Grid>
                <Grid item>
                    <ExpandConnectionsButton />
                </Grid>
            </Grid>

        </ThemeProvider>

    )
} 

export default function ComponentConnectionVisualizer() {

    const elements = [
        {
            id: '1',
            connectable: false,
            data: { label: (
                <ComponentNode
                    name={"COMP-2"}
                />
            ) },
            position: { x: 250, y: 25 },
        },
        // default node
        {
            id: '2',
            // you can also pass a React component as a label
            data: { label: (
                <ComponentNode
                    name={"COMP-1"}
                />
            ) },
            position: { x: 100, y: 125 },
        },
        {
            id: '3',
            data: { label: (
                <ComponentNode
                    name={"COMP-3"}
                />
            ) },
            position: { x: 250, y: 250 },
        },
        // animated edge
        { id: 'e1-2', source: '1', target: '2', animated: true },
        { id: 'e2-3', source: '2', target: '3' },
    ];

    return (
        <Grid 
            container 
            direction="column"
            justifyContent="flex-start"
            alignItems="center"
            spacing={2}
        >

            <Grid item>
                <OptionsPanel>
                    <Grid container
                        direction="row"
                        justifyContent="center"
                        alignItems="flex-end"
                        spacing={2}
                    >
                        <Grid item>
                            <ComponentAutocomplete 
                                onSelect={() => {}} 
                            />
                        </Grid>
                        <Grid item>
                            <TextField
                                required
                                id="datetime-local"
                                label="Time"
                                type="datetime-local"
                                sx={{ width: 240 }}
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                size="large"
                                onChange={(event) => {
                                    let date = new Date(event.target.value);
                                    //setTime(Math.round(date.getTime() / 1000));
                                }}
                            />
                        </Grid>
                        
                    </Grid>
                </OptionsPanel>
            </Grid>

            <Grid item>
                <VisualizerPanel>
                    <ReactFlow 
                        elements={elements}
                        nodesConnectable={false}
                    >
                        <Background
                            variant="dots"
                            gap={12}
                            size={0.5}
                        />
                        <Controls />
                    </ReactFlow>
                </VisualizerPanel>
            </Grid>

        </Grid>

    )

}