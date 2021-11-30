import React, { useState, useEffect } from 'react';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Divider from '@mui/material/Divider';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EventIcon from '@mui/icons-material/Event';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import CommentIcon from '@mui/icons-material/Comment';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import createTheme from '@mui/material/styles/createTheme';
import styled from '@mui/material/styles/styled';

import ComponentEvent from './ComponentEvent.js';

import { unixTimeToString } from './utility/utility.js';

import { Link } from "react-router-dom";

import {
    useParams
} from "react-router-dom";

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

const MarginDivider = styled(Divider)(({ theme }) => ({
    marginTop: theme.spacing(1),
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
                    color: "rgba(0,0,0, 0.4)"
                }}
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

const theme = createTheme();

function ComponentPage() {
    let { name } = useParams();

    // the list of components in objects representation
    const [component, setComponent] = useState(undefined);

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
                >
                    <AccordionSummary>
                        Properties   
                    </AccordionSummary>
                    <AccordionDetails>
                        {properties_content}
                    </AccordionDetails>
                </Accordion>

                <Accordion
                    style={{
                        marginTop: theme.spacing(1)
                    }}
                >
                    <AccordionSummary>
                        Connections
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