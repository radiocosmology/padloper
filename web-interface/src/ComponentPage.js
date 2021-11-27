import React, { useState, useEffect } from 'react';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableHead from '@mui/material/TableHead';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
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
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
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

const EntryRowLabel = styled((props) => (
    <Paper 
        elevation={0}
        {...props}
    />
))(({ theme }) => ({
    backgroundColor: 'rgba(0, 0, 0, .05)',
    width: '80px',
    marginRight: theme.spacing(4),
}));

const theme = createTheme();


// helper functions

// takes UNIX time in seconds
function unixToString(UNIX_timestamp, includeTime){
    let a = new Date(UNIX_timestamp * 1000);
    let months = [
        'Jan','Feb','Mar','Apr','May','Jun','Jul',
        'Aug','Sep','Oct','Nov','Dec'
    ];
    let year = a.getFullYear();
    let month = months[a.getMonth()];
    let date = a.getDate();
    let hour = a.getHours();
    let min = a.getMinutes();
    let sec = a.getSeconds();

    let time = `${date} ${month} ${year}`;
    if (includeTime) {
        time += `, ${hour}:${min}:${sec}`;
    }
    return time;
}

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

        let properties_content = (
            <Stack spacing={1}>
                {component.properties.map((prop) => (
                    <EntryAccordion>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <EventIcon fontSize="small" />
                                <div>
                                    {unixToString(prop.start_time, false)} 
                                </div>
                                {prop.end_time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>
                                            -
                                        </div> 
                                        <div>
                                            {unixToString(prop.end_time, false)}
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
                                <Stack direction='row' spacing={1}>

                                    <EntryRowLabel>Start</EntryRowLabel>

                                    <AccessTimeIcon fontSize="small"/>
                                    <div>
                                        {unixToString(prop.start_time, true)}
                                    </div>

                                    <PersonIcon 
                                        fontSize="small"
                                        style={{
                                            marginLeft:theme.spacing(3),
                                        }}
                                    />
                                    <div>
                                        {prop.start_uid} ({unixToString(
                                            prop.start_edit_time, false)
                                        })
                                    </div>

                                    <CommentIcon 
                                        fontSize="small"
                                        style={{
                                            marginLeft:theme.spacing(3),
                                        }}
                                    />
                                    <div>
                                        {prop.start_comments == '' ? '—' :
                                        prop.start_comments}
                                    </div>


                                </Stack>

                                <Stack direction='row' spacing={1}>

                                    <EntryRowLabel>End</EntryRowLabel>

                                    <AccessTimeIcon fontSize="small"/>
                                    <div>
                                        {
                                            prop.end_time <= 
                                            Number.MAX_SAFE_INTEGER ? 
                                            unixToString(prop.end_time, true) :
                                            '—'
                                        }
                                    </div>

                                    <PersonIcon 
                                        fontSize="small"
                                        style={{
                                            marginLeft:theme.spacing(3),
                                        }}
                                    />
                                    <div>
                                        {
                                            prop.end_uid == '' ? '—' :
                                            `${prop.end_uid} (${unixToString(
                                                prop.end_edit_time, false)})`
                                        }
                                    </div>

                                    <CommentIcon 
                                        fontSize="small"
                                        style={{
                                            marginLeft: theme.spacing(3),
                                        }}
                                    />
                                    <div>
                                        {prop.end_comments == '' ? '—' :
                                        prop.end_comments}
                                    </div>


                                </Stack>
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