import React, { useState, useEffect } from 'react';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EventIcon from '@mui/icons-material/Event';
import AddIcon from '@mui/icons-material/Add';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import createTheme from '@mui/material/styles/createTheme';
import styled from '@mui/material/styles/styled';

import ComponentEvent from './ComponentEvent.js';
import ComponentPropertyAddPanel from './ComponentPropertyAddPanel.js';

import { unixTimeToString } from './utility/utility.js';

import { Link } from "react-router-dom";

import {
    useParams
} from "react-router-dom";
import { Typography } from '@mui/material';

const Root = styled(Paper)(({ theme }) => ({
    marginTop: theme.spacing(1),
    padding: theme.spacing(1),
    width: '1000px',
    maxWidth: '100%',
    marginLeft: 'auto',
    marginRight: 'auto',
    textAlign: 'center',
}));

const ComponentNameWrapper = styled(Paper)(({ theme }) => ({
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.common.white,
    margin: 'auto',
    marginLeft: 0,
    marginRight: theme.spacing(1),
    marginBottom: theme.spacing(1),
    width: '300px',
    height: '200px',
    fontSize: '300%',
    lineHeight: '200px',
}));

const Accordion = styled((props) => (
    <MuiAccordion 
        disableGutters 
        elevation={0} 
        defaultExpanded
        {...props} 
    />
))(({ theme }) => ({
    borderBottom: `1px solid ${theme.palette.divider}`,
}));

const EntryAccordion = styled((props) => (
    <Accordion 
        defaultExpanded={false}
        {...props}
    />
))(({ theme }) => ({
    borderBottom: `0`,
}));

const AccordionSummary = styled((props) => (
    <MuiAccordionSummary
        expandIcon={
            <ExpandMoreIcon 
                sx={{
                    color: "rgba(0,0,0, 0.4)",
                    padding: "4px",
                }}
                onClick={props.expandOnClick}
            />
        }
      {...props}
    />
))(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .06)',
    flexDirection: 'row-reverse',
    '& .MuiAccordionSummary-content': {
      marginLeft: theme.spacing(1),
    },
    lineHeight: '100%',
    display: 'flex',
}));

const EntryAccordionSummary = styled(AccordionSummary)(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .04)',
    flexDirection: 'row',
    '& .MuiAccordionSummary-content': {
      marginLeft: theme.spacing(1),
    },
}));

const AccordionDetails = styled(MuiAccordionDetails)(({ theme }) => ({
    padding: theme.spacing(2),
    borderTop: '1px solid rgba(0, 0, 0, .125)',
}));

const EntryAccordionDetails = styled(AccordionDetails)(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .015)',
}));

const AddButton = styled((props) => (
    <Button 
        variant="outlined"
        size="small"
        style={{
            margin: '-4px',
        }}
        {...props}
    >
        <AddIcon />
    </Button>
))(({ theme }) => ({
    marginTop: -2 * theme.spacing(2),
}));

const theme = createTheme();

function ComponentPage() {
    let { name } = useParams();

    // the list of components in objects representation
    const [component, setComponent] = useState(undefined);

    const [
        open_properties_accordion, setOpenPropertiesAccordion
    ] = useState(true);
    const [
        open_connections_accordion, setOpenConnectionsAccordion
    ] = useState(true);
    const [
        open_properties_add_panel, setOpenPropertiesAddPanel
    ] = useState(false);

    const toggleOpenPropertiesAccordion = () => {
        setOpenPropertiesAccordion(!open_properties_accordion);
    }

    const toggleOpenConnectionsAccordion = () => {
        setOpenConnectionsAccordion(!open_connections_accordion);
    }

    useEffect(() => {
        fetch(`/api/components_name/${name}`).then(
            res => res.json()
        ).then(data => {
            data.result.properties.sort(
                (a, b) => parseFloat(a.start_time) - parseFloat(b.start_time)
            );
            data.result.connections.sort(
                (a, b) => parseFloat(a.start_time) - parseFloat(b.start_time)
            );
            setComponent(data.result);
        });
    }, [name]);

    let content = (
        <>
            Loading...
        </>
    )

    if (component) {

        let properties_add_panel_content = (open_properties_add_panel) ? (
            <ComponentPropertyAddPanel 
                theme={theme} 
                onClose={() => setOpenPropertiesAddPanel(false)}
            />
        ) : <></>;

        let properties_content = (
            <Stack spacing={1}>
                {component.properties.map((prop) => (
                    <EntryAccordion>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <EventIcon fontSize="small" />
                                <div>
                                    {unixTimeToString(prop.start_time, false)} 
                                </div>
                                {prop.end_time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>-</div> 
                                        <div>
                                            {unixTimeToString(
                                                prop.end_time, false
                                            )}
                                        </div> 
                                    </>
                                ) : ''}
                                <strong
                                    style={{
                                        marginLeft: theme.spacing(4)
                                    }}
                                >
                                    {prop.type.name}
                                </strong>
                                <div>
                                    =
                                </div>
                                <strong>{prop.values}</strong>
                            </Stack>
                        
                        </EntryAccordionSummary>
                        <EntryAccordionDetails>
                            <Stack spacing={1}>
                                <ComponentEvent
                                    name="Start"
                                    time={prop.start_time}
                                    uid={prop.start_uid}
                                    edit_time={prop.start_edit_time}
                                    comments={prop.start_comments}
                                    theme={theme} />

                                {
                                    prop.end_time <= 
                                    Number.MAX_SAFE_INTEGER ?
                                    <ComponentEvent
                                        name="End"
                                        time={prop.end_time}
                                        uid={prop.end_uid}
                                        edit_time={prop.end_edit_time}
                                        comments={prop.end_comments}
                                        theme={theme} />
                                    : ""
                                }
                            </Stack>
                        </EntryAccordionDetails>
                    </EntryAccordion>
                ))}
            </Stack>
        )

        let connections_content = (
            <Stack spacing={1}>
                {component.connections.map((conn) => (
                    <EntryAccordion>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <EventIcon fontSize="small" />
                                <div>
                                    {unixTimeToString(conn.start_time, false)} 
                                </div>
                                {conn.end_time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>—</div> 
                                        <div>
                                            {unixTimeToString(
                                                conn.end_time, false
                                            )}
                                        </div> 
                                    </>
                                ) : ''}
                                <strong
                                    style={{
                                        marginLeft: theme.spacing(4)
                                    }}
                                >
                                    {
                                        <Link to={`/component/${name}`}>
                                            {name}
                                        </Link>
                                    } — {
                                        <Link to={`/component/${conn.name}`}>
                                        {conn.name}
                                    </Link>}
                                </strong>
                            </Stack>
                        
                        </EntryAccordionSummary>
                        <EntryAccordionDetails>
                            <Stack spacing={1}>
                                <ComponentEvent
                                    name="Start"
                                    time={conn.start_time}
                                    uid={conn.start_uid}
                                    edit_time={conn.start_edit_time}
                                    comments={conn.start_comments}
                                    theme={theme} />

                                {
                                    conn.end_time <= 
                                    Number.MAX_SAFE_INTEGER ?
                                    <ComponentEvent
                                        name="End"
                                        time={conn.end_time}
                                        uid={conn.end_uid}
                                        edit_time={conn.end_edit_time}
                                        comments={conn.end_comments}
                                        theme={theme} />
                                    : ""
                                }
                            </Stack>
                        </EntryAccordionDetails>
                    </EntryAccordion>
                ))}
            </Stack>
        )

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

                <Accordion
                    style={{
                        marginTop: theme.spacing(1)
                    }}
                    expanded={open_properties_accordion}
                >
                    <AccordionSummary
                        expandOnClick={toggleOpenPropertiesAccordion}
                    >
                        
                        <Typography style={{ flex: 1 }} align='left'>
                            Properties
                        </Typography>
                           

                        <AddButton 
                            onClick={
                                () => {setOpenPropertiesAddPanel(true)}
                            }
                        />

                    </AccordionSummary>
                    <AccordionDetails>
                        {properties_add_panel_content}
                        
                        {properties_content}
                    </AccordionDetails>
                </Accordion>

                <Accordion
                    style={{
                        marginTop: theme.spacing(1)
                    }}
                    expanded={open_connections_accordion}
                >
                    <AccordionSummary
                        expandOnClick={toggleOpenConnectionsAccordion}
                    >
                        <Typography style={{ flex: 1 }} align='left'>
                            Connections
                        </Typography>

                        <AddButton />
                    
                    </AccordionSummary>
                    <AccordionDetails>
                        {connections_content}
                    </AccordionDetails>
                </Accordion>

            </ThemeProvider>
        )
    }

    return (
        <Root>
            {content}
        </Root>
    )
}

export default ComponentPage;