import React, { useState, useEffect } from 'react';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import EventIcon from '@mui/icons-material/Event';
import AddIcon from '@mui/icons-material/Add';

import ThemeProvider from '@mui/material/styles/ThemeProvider';
import createTheme from '@mui/material/styles/createTheme';
import styled from '@mui/material/styles/styled';

import Timestamp from './Timestamp.js';
import ComponentEvent from './ComponentEvent.js';
import ComponentPropertyAddPanel from './ComponentPropertyAddPanel.js';
import ComponentConnectionAddPanel from './ComponentConnectionAddPanel.js';

import { Link } from "react-router-dom";

import {
    useParams
} from "react-router-dom";
import { Typography } from '@mui/material';

/**
 * A styled Paper component that represents the root for the component page.
 */
const Root = styled(Paper)(({ theme }) => ({
    marginTop: theme.spacing(1),
    padding: theme.spacing(1),
    width: '1000px',
    maxWidth: '100%',
    marginLeft: 'auto',
    marginRight: 'auto',
    textAlign: 'center',
}));

/**
 * A styled Paper component that wraps around the cool big name 
 * of the component.
 */
const ComponentNameWrapper = styled((props) => (
    <Paper
        elevation={1} 
        {...props}
    />
))(({ theme }) => ({
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.common.white,
    margin: 'auto',
    marginLeft: 0,
    marginRight: theme.spacing(1),
    marginBottom: theme.spacing(1),
    width: '450px',
    height: '200px',
    fontSize: '300%',
    lineHeight: '200px',
}));

/**
 * A styling for an MUI Accordion component.
 */
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

/**
 * An even more styled Accordion component.
 */
const EntryAccordion = styled((props) => (
    <Accordion 
        defaultExpanded={false}
        {...props}
    />
))(({ theme }) => ({
    borderBottom: `0`,
}));

/**
 * A styled MUI AccordionSummary component
 */
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

/**
 * A MUI component representing a button for adding a component.
 */
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

/**
 * Custom MUI theme, see 
 * https://mui.com/customization/theming/#theme-configuration-variables
 */
const theme = createTheme({
    typography: {
        body2: {
            fontWeight: 800,
            fontSize: 16,
        },
    }
});

/**
 * A MUI component representing a component page.
 */
function ComponentPage() {
    // the name of the component to look at, which is fed through the URL
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
    const [
        open_connections_add_panel, setOpenConnectionsAddPanel
    ] = useState(false);

    // toggle the properties accordion.
    const toggleOpenPropertiesAccordion = () => {
        setOpenPropertiesAccordion(!open_properties_accordion);
    }

    // toggle the connections accordion.
    const toggleOpenConnectionsAccordion = () => {
        setOpenConnectionsAccordion(!open_connections_accordion);
    }

    /**
     * variable and toggle for reloading the page. 
     * When toggled, reload everything
     */
    const [reloadBool, setReloadBool] = useState(false);
    function toggleReload() {
        setReloadBool(!reloadBool);
    }

    /**
     * Set a property for the component.
     * @param {string} propertyType - the name of the property tyoe
     * @param {int} time - the time at which to add the property 
     * @param {string} uid - the ID of the user that is adding the property
     * @param {string} comments - the comments associated with the property 
     * @param {Array} values - an array connecting the values of the property. 
     */
    async function setProperty(propertyType, time, uid, comments, values) {

        // build up the string to query the API
        let input = `/api/component_set_property`;
        input += `?name=${name}`;
        input += `&propertyType=${propertyType}`;
        input += `&time=${time}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;
        input += `&valueCount=${values.length}`;
        input += `&values=`;
        for (let val of values) {
            input += `${val};`;
        }
        input = input.substring(0, input.length - 1);

        fetch(input).then(
            res => res.json()
        ).then(data => {
            setOpenPropertiesAddPanel(false);
            toggleReload();
        });
    }

    /**
     * Add a connection to another component.
     * @param {string} otherName - the name of the other component 
     * for the connection
     * @param {int} time - the time to make the connection at 
     * @param {string} uid - the ID of the user that is making the connection 
     * @param {string} comments - the comments associated with the connection 
     * @returns 
     */
    async function addConnection(otherName, time, uid, comments) {
        
        // build up the string to query the API
        let input = `/api/component_add_connection`;
        input += `?name1=${name}`;
        input += `&name2=${otherName}`;
        input += `&time=${time}`;
        input += `&uid=${uid}`;
        input += `&comments=${comments}`;

        return new Promise((resolve, reject) => {
            fetch(input).then(
                res => res.json()
            ).then(data => {
                if (data.result) {
                    setOpenConnectionsAddPanel(false);
                    toggleReload();
                }
                resolve(data.result);
            });
        });

    }

    /**
     * When the name of the component is changed or the page is to be reloaded,
     * reload the page, query the API to query the component again,
     * and sort all the properties and connections by their start time.
     */
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
    }, [name, reloadBool]);

    /**
     * Default value for the content.
     */
    let content = (
        <>
            Loading...
        </>
    )

    /**
     * When the component is loaded, create the properties and connections
     * accordions.
     */
    if (component) {

        let properties_add_panel_content = (open_properties_add_panel) ? (
            <ComponentPropertyAddPanel 
                theme={theme} 
                onClose={() => setOpenPropertiesAddPanel(false)}
                onSet={setProperty}
            />
        ) : <></>;

        let properties_content = (
            <Stack spacing={1}>
                {component.properties.map((prop) => (
                    <EntryAccordion>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <EventIcon fontSize="small" />
                                <Timestamp unixTime={prop.start_time} />
                                {prop.end_time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>-</div> 
                                        <Timestamp unixTime={prop.end_time} />
                                    </>
                                ) : ''}
                                <Typography
                                    variant="body2"
                                    style={{
                                        marginLeft: theme.spacing(4)
                                    }}
                                >
                                    {prop.type.name} = { '[ ' +
                                        prop.values.map(
                                            el => el + ` ${
                                            (prop.type.units === undefined) ? 
                                                '' : prop.type.units
                                            }`
                                        ).join(", ") + ' ]'
                                    }
                                </Typography>
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

        let connections_add_panel_content = (open_connections_add_panel) ? (
            <ComponentConnectionAddPanel 
                theme={theme} 
                onClose={() => setOpenConnectionsAddPanel(false)}
                onSet={addConnection}
                name={name}
            />
        ) : <></>;

        let connections_content = (
            <Stack spacing={1}>
                {component.connections.map((conn) => (
                    <EntryAccordion>
                        <EntryAccordionSummary>
                            <Stack spacing={1} direction="row">
                                <EventIcon fontSize="small" />
                                <Timestamp unixTime={conn.start_time} />
                                {conn.end_time <= Number.MAX_SAFE_INTEGER ? (
                                    <>
                                        <div>—</div> 
                                        <Timestamp unixTime={conn.end_time} />
                                    </>
                                ) : ''}
                                <Typography
                                    variant="body2"
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
                                </Typography>
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
                    <Grid container spacing={2} justifyContent="space-around">
                        <Grid item>
                            <Stack spacing={-0.1}>
                                <Typography color={'rgb(128,128,128)'}>
                                    Component type
                                </Typography>
                                <Typography variant="h5">
                                    {component.type.name}
                                </Typography>
                            </Stack>
                        </Grid>
                        <Grid item>
                            <Stack spacing={-0.1}>
                                <Typography color={'rgb(128,128,128)'}>
                                    Component version
                                </Typography>
                                <Typography variant="h5">
                                    {component.version.name}
                                </Typography>
                            </Stack>
                        </Grid>
                        <Grid item>
                            <Stack spacing={-0.1}>
                                <Typography color={'rgb(128,128,128)'}>
                                    Date added
                                </Typography>
                                <Timestamp 
                                    unixTime={component.time_added} 
                                    variant="h5"
                                />
                            </Stack>
                        </Grid>
                    </Grid>
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

                        <AddButton 
                            onClick={
                                () => {setOpenConnectionsAddPanel(true)}
                            }
                        />
                    
                    </AccordionSummary>
                    <AccordionDetails>
                        {connections_add_panel_content}

                        {connections_content}
                    </AccordionDetails>
                </Accordion>

            </ThemeProvider>
        )
    }

    // return all the good stuff
    return (
        <Root>
            {content}
        </Root>
    )
}

export default ComponentPage;
